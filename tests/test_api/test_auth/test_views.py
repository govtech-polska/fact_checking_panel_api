from datetime import timedelta
from unittest import mock
from uuid import uuid4

import pytest
from assertpy import assert_that
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authtoken.models import Token

from dook.api.auth.exceptions import (
    InternalEmailErrorException,
    InvalidInviteTokenException,
    InvitationAlreadyExistException,
    MissingDomainForSpecialistInvitationException,
    TokenAlreadyUsedException,
    UserAlreadyExistException,
)
from dook.api.news.exceptions import DomainDoesNotExistException
from dook.core.users.constants import (
    InvitationStatusType,
    InvitationUserRoleType,
    UserRoleType,
)
from dook.core.users.models import Invitation, User
from dook.core.users.tokens import password_reset_token_generator
from tests.factories.news import DomainFactory
from tests.factories.users import InvitationFactory, UserFactory


class TestSignUpView:
    @pytest.fixture
    def default_user_data(self):
        return {
            "name": "test_user",
            "password": "Test1234!",
            "password2": "Test1234!",
            "specialization": "other",
        }

    @pytest.mark.django_db
    def test_success_registration(self, default_user_data, api_client):
        with mock.patch.multiple(
            "dook.api.auth.views", send_registration_confirmation_email=mock.DEFAULT
        ) as mocked:
            invitation = InvitationFactory()
            assert invitation.status == InvitationStatusType.WAITING
            url = reverse(f"auth:sign_up", kwargs={"token": invitation.token})
            response = api_client.post(url, default_user_data, format="json")

            assert response.status_code == 201

            email_args = {"name": default_user_data["name"], "email": invitation.email}
            mocked["send_registration_confirmation_email"].assert_called_with(
                **email_args
            )

            user = User.objects.filter(email=invitation.email).first()

            assert user.is_active is True
            assert user.is_admin is False
            assert user.role == UserRoleType.FACT_CHECKER

            invitation = Invitation.objects.filter(email=user.email).first()
            assert invitation.status == InvitationStatusType.USED

            # Specialist invitation
            domain = DomainFactory()
            invitation = InvitationFactory(
                user_role=UserRoleType.SPECIALIST, domain=domain
            )
            url = reverse(f"auth:sign_up", kwargs={"token": invitation.token})
            response = api_client.post(url, default_user_data, format="json")

            assert response.status_code == status.HTTP_201_CREATED
            user = User.objects.filter(email=invitation.email).first()

            assert user.role == UserRoleType.SPECIALIST
            assert user.domain.id == domain.id

    @pytest.mark.django_db
    def test_registration_with_invalid_token(self, default_user_data, api_client):
        url = reverse(f"auth:sign_up", kwargs={"token": "1111"})
        response = api_client.post(url, default_user_data, format="json")

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to(
            InvalidInviteTokenException.default_code
        )

    @pytest.mark.django_db
    def test_registration_with_used_token(self, default_user_data, api_client):
        with mock.patch.multiple(
            "dook.api.auth.views", send_registration_confirmation_email=mock.DEFAULT
        ) as mocked:
            invitation = InvitationFactory(status=InvitationStatusType.USED)

            url = reverse(f"auth:sign_up", kwargs={"token": invitation.token})
            response = api_client.post(url, default_user_data, format="json")

            assert response.status_code == 400
            assert_that(response.data["detail"].code).is_equal_to(
                TokenAlreadyUsedException.default_code
            )

    @pytest.mark.django_db
    def test_check_token(self, api_client):
        invitation = InvitationFactory()
        url = reverse(f"auth:sign_up", kwargs={"token": invitation.token})
        response = api_client.get(url)

        assert response.status_code == 200

        url = reverse(f"auth:sign_up", kwargs={"token": "2222"})

        response = api_client.get(url)

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to(
            InvalidInviteTokenException.default_code
        )


@pytest.mark.django_db
class TestCreateTokenView:
    url = reverse("auth:login")
    login_data = {"email": "test@dook.pro", "password": "password"}

    def test_success_obtain_token(self, api_client):
        user = UserFactory(email=self.login_data["email"])
        user.set_password(self.login_data["password"])
        user.save()

        response = api_client.post(self.url, self.login_data)

        assert response.status_code == 200
        assert_that(response.data).contains("token")

    def test_inactive_account(self, api_client):
        user = UserFactory(email=self.login_data["email"], is_verified=False)
        user.set_password(self.login_data["password"])
        user.save()

        response = api_client.post(self.url, self.login_data)

        assert response.status_code == 403
        assert_that(response.data["detail"].code).is_equal_to("email_not_verified")

    def test_invalid_credentials(self, api_client):
        password = self.login_data["password"]
        user = UserFactory(email=self.login_data["email"])
        user.set_password(password)
        user.save()

        response = api_client.post(
            self.url, data={**self.login_data, **{"password": f"{password}_invalid"}}
        )

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to("invalid_credentials")

    def refresh_token_for_each_login(self, api_client):
        assert Token.objects.count() == 0

        user = UserFactory(email=self.login_data["email"])
        user.set_password(self.login_data["password"])
        user.save()

        response = api_client.post(self.url, data=self.login_data)

        assert Token.objects.count() == 1
        old_token_id = Token.objects.first().id
        assert response.json() == str(old_token_id)

        response = api_client.post(self.url, data=self.login_data)

        assert Token.objects.count() == 1
        token_id = Token.objects.first().id
        assert old_token_id != token_id
        assert response.json() == str(token_id)


@pytest.mark.django_db
class TestLogoutView:
    url = reverse("auth:logout")

    def test_logout(self, authenticated_api_client):
        response = authenticated_api_client.post(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestCreateInvitationView:
    url = reverse("auth:send_invite")

    @pytest.fixture
    def default_invitation_data(self):
        return {
            "email": "test@email.com",
            "user_role": InvitationUserRoleType.FACT_CHECKER,
        }

    def test_success_invitation(self, admin_api_client, default_invitation_data):
        with mock.patch.multiple(
            "dook.core.users.models", send_registration_invitation_email=mock.DEFAULT
        ) as mocked:
            mocked["send_registration_invitation_email"].return_value = True

            response = admin_api_client.post(self.url, default_invitation_data)

            invitation = Invitation.objects.filter(
                email=default_invitation_data["email"]
            ).first()
            invite_url = (
                f"https://{settings.PANEL_DOMAIN_NAME}/register/{invitation.token}"
            )

            assert response.status_code == 201
            assert invitation
            assert_that(invitation.status).is_equal_to(InvitationStatusType.WAITING)

            email_args = {"email": invitation.email, "invite_url": invite_url}
            mocked["send_registration_invitation_email"].assert_called()
            mocked["send_registration_invitation_email"].assert_called_with(**email_args)

    @pytest.mark.parametrize(
        "sent_at, expected_status",
        (
            (
                timezone.now() - timedelta(days=settings.INVITATION_EXPIRY + 1),
                status.HTTP_201_CREATED,
            ),
            (
                timezone.now() - timedelta(days=settings.INVITATION_EXPIRY - 1),
                status.HTTP_400_BAD_REQUEST,
            ),
        ),
    )
    def test_resend_invitation(self, admin_api_client, sent_at, expected_status):
        with mock.patch.multiple(
            "dook.core.users.models", send_registration_invitation_email=mock.DEFAULT
        ) as mocked:
            mocked["send_registration_invitation_email"].return_value = True

            invitation = InvitationFactory(sent_at=sent_at)

            response = admin_api_client.post(
                self.url,
                data={
                    "email": invitation.email,
                    "user_role": InvitationUserRoleType.FACT_CHECKER,
                },
            )

            assert response.status_code == expected_status
            if response.status_code == status.HTTP_400_BAD_REQUEST:
                assert (
                    response.data["detail"].code
                    == InvitationAlreadyExistException.default_code
                )

    def test_user_exists_in_system(self, admin_api_client):
        user = UserFactory(role=UserRoleType.SPECIALIST)

        response = admin_api_client.post(
            self.url,
            data={"email": user.email, "user_role": InvitationUserRoleType.FACT_CHECKER},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"].code == UserAlreadyExistException.default_code

    def test_email_error(self, admin_api_client, default_invitation_data):
        with mock.patch.multiple(
            "dook.core.users.models", send_registration_invitation_email=mock.DEFAULT
        ) as mocked:
            mocked["send_registration_invitation_email"].return_value = False

            response = admin_api_client.post(self.url, default_invitation_data)

            invitation = Invitation.objects.filter(
                email=default_invitation_data["email"]
            ).first()

            assert response.status_code == 503

            assert_that(invitation).is_none()
            assert_that(response.data["detail"].code).is_equal_to(
                InternalEmailErrorException.default_code
            )

    def test_without_permissions(self, api_client, default_invitation_data):
        response = api_client.post(self.url, default_invitation_data)

        assert response.status_code == 401

    def test_specialist_role_invitation(self, admin_api_client):
        with mock.patch(
            "dook.core.users.models.send_registration_invitation_email"
        ) as mocked:
            mocked.return_value = True
            payload = {"email": "test@email.com", "user_role": UserRoleType.SPECIALIST}

            response = admin_api_client.post(self.url, payload)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                response.data["detail"].code
                == MissingDomainForSpecialistInvitationException.default_code
            )

            payload = {**payload, **{"domain": str(DomainFactory().pk)}}
            response = admin_api_client.post(self.url, payload)

            assert response.status_code == status.HTTP_201_CREATED

            payload["domain"] = uuid4()
            response = admin_api_client.post(self.url, payload)

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert (
                response.data["detail"].code == DomainDoesNotExistException.default_code
            )


class TestPasswordResetRequestView:
    @pytest.mark.django_db
    def test_success_request(self, api_client):
        with mock.patch.multiple(
            "dook.api.auth.views", send_password_reset_email=mock.DEFAULT
        ) as mocked:
            mocked["send_password_reset_email"].return_value = True
            user = UserFactory(email="test@dook.pro")

            url = reverse(f"auth:password_reset_request")
            response = api_client.post(url, {"email": user.email}, format="json")

            assert response.status_code == 200

            reset_url = password_reset_token_generator.make_url(user)

            assert mocked["send_password_reset_email"].called
            assert mocked["send_password_reset_email"].with_args(user.email, reset_url)

    @pytest.mark.django_db
    def test_request_invalid_email(self, api_client):
        with mock.patch.multiple(
            "dook.api.auth.views", send_password_reset_email=mock.DEFAULT
        ) as mocked:
            url = reverse(f"auth:password_reset_request")
            response = api_client.post(url, {"email": "some@email.com"}, format="json")

            assert response.status_code == 200
            assert mocked["send_password_reset_email"].called is False


class TestPasswordResetView:
    @pytest.fixture
    def default_reset_data(self):
        user = UserFactory(email="test@dook.pro")
        token = password_reset_token_generator.make_token(user=user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return {"user": user, "token": token, "uid": uid}

    @pytest.mark.django_db
    def test_success_reset_get(self, api_client, default_reset_data):
        url = reverse(
            f"auth:password_reset",
            kwargs={
                "uidb64": default_reset_data["uid"],
                "token": default_reset_data["token"],
            },
        )
        response = api_client.get(url, format="json")

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_success_reset_post(self, api_client, default_reset_data):
        url = reverse(
            f"auth:password_reset",
            kwargs={
                "uidb64": default_reset_data["uid"],
                "token": default_reset_data["token"],
            },
        )
        new_password = "Password54321!"
        data = {"password": new_password, "password2": new_password}
        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert_that(default_reset_data["user"].check_password(raw_password=new_password))

    @pytest.mark.django_db
    def test_user_does_not_exist(self, api_client, default_reset_data):
        url = reverse(
            f"auth:password_reset",
            kwargs={
                "uidb64": "MWU2NzUzMzMtMWJmMC00OTJjLWE2YzMtMGY4OTE5MmE1MGNl",
                "token": default_reset_data["token"],
            },
        )
        new_password = "Password54321!"
        data = {"password": new_password, "password2": new_password}
        response = api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to("invalid_token_error")

    @pytest.mark.django_db
    def test_invalid_token(self, api_client, default_reset_data):
        url = reverse(
            f"auth:password_reset",
            kwargs={
                "uidb64": default_reset_data["uid"],
                "token": "5ff-4409af0e1e600a7c78f9",
            },
        )
        new_password = "Password54321!"
        data = {"password": new_password, "password2": new_password}
        response = api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to("invalid_token_error")
        assert_that(
            default_reset_data["user"].check_password(raw_password=new_password)
        ).is_false()


class TestInternalPasswordResetView:
    @pytest.mark.django_db
    def test_success_reset(self, authenticated_api_client, default_user):
        url = reverse("auth:internal_password_reset",)
        new_password = "Password54321!"
        data = {
            "old_password": "password",
            "password": new_password,
            "password2": new_password,
        }
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == 200

        user = User.objects.filter(id=default_user.id).first()
        assert_that(user.check_password(new_password)).is_true()

    @pytest.mark.django_db
    def test_wrong_old_password(self, authenticated_api_client, default_user):
        url = reverse("auth:internal_password_reset",)
        new_password = "Password54321!"
        data = {
            "old_password": "wrongpassword",
            "password": new_password,
            "password2": new_password,
        }
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert_that(default_user.check_password(new_password)).is_false()
