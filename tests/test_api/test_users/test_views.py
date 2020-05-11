from unittest import mock
from uuid import uuid4

import pytest
from assertpy import assert_that
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from dook.api.users.exceptions import (
    InternalEmailErrorException,
    InvalidInviteTokenException,
    TokenAlreadyUsedException
)
from dook.core.users.constants import (
    InvitationStatusType,
    InvitationUserRoleType,
    UserRoleType,
)
from dook.core.users.models import Invitation, User
from dook.core.users.tokens import password_reset_token_generator
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
            "dook.api.users.views", send_registration_confirmation_email=mock.DEFAULT
        ) as mocked:
            invitation = InvitationFactory()
            assert invitation.status == InvitationStatusType.WAITING
            url = reverse(f"users:sign_up", kwargs={"token": invitation.token})
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

    @pytest.mark.django_db
    def test_registration_with_invalid_token(self, default_user_data, api_client):
        url = reverse(f"users:sign_up", kwargs={"token": "1111"})
        response = api_client.post(url, default_user_data, format="json")

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to(
            InvalidInviteTokenException.default_code
        )

    @pytest.mark.django_db
    def test_registration_with_used_token(self, default_user_data, api_client):
        with mock.patch.multiple(
            "dook.api.users.views", send_registration_confirmation_email=mock.DEFAULT
        ) as mocked:
            invitation = InvitationFactory(status=InvitationStatusType.USED)

            url = reverse(f"users:sign_up", kwargs={"token": invitation.token})
            response = api_client.post(url, default_user_data, format="json")

            assert response.status_code == 400
            assert_that(response.data["detail"].code).is_equal_to(
                TokenAlreadyUsedException.default_code
            )

    @pytest.mark.django_db
    def test_check_token(self, api_client):
        invitation = InvitationFactory()
        url = reverse(f"users:sign_up", kwargs={"token": invitation.token})
        response = api_client.get(url)

        assert response.status_code == 200

        url = reverse(f"users:sign_up", kwargs={"token": "2222"})

        response = api_client.get(url)

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to(
            InvalidInviteTokenException.default_code
        )


class TestCreateTokenView:
    @pytest.mark.django_db
    def test_success_obtain_token(self, api_client):
        user = UserFactory(email="test@dook.pro")
        user.set_password("password")
        user.save()
        data = {"email": "test@dook.pro", "password": "password"}

        url = reverse(f"users:login")
        response = api_client.post(url, data)

        assert response.status_code == 200
        assert_that(response.data).contains("token")

    @pytest.mark.django_db
    def test_inactive_account(self, api_client):
        user = UserFactory(email="test@dook.pro", is_verified=False)
        user.set_password("password")
        user.save()

        data = {"email": "test@dook.pro", "password": "password"}

        url = reverse(f"users:login")
        response = api_client.post(url, data)

        assert response.status_code == 403
        assert_that(response.data["detail"].code).is_equal_to("email_not_verified")

    @pytest.mark.django_db
    def test_invalid_credentials(self, api_client):
        user = UserFactory(email="test@dook.pro")
        user.set_password("password")
        user.save()

        data = {"email": "test@dook.pro", "password": "wrongpassword"}

        url = reverse(f"users:login")
        response = api_client.post(url, data)

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to("invalid_credentials")


class TestCreateInvitationView:
    @pytest.fixture
    def default_invitation_data(self):
        return {
            "email": "test@email.com",
            "user_role": InvitationUserRoleType.FACT_CHECKER,
        }

    @pytest.mark.django_db
    def test_success_invitation(self, admin_api_client, default_invitation_data):
        with mock.patch.multiple(
            "dook.core.users.models", send_registration_invitation_email=mock.DEFAULT
        ) as mocked:
            mocked["send_registration_invitation_email"].return_value = True

            url = reverse(f"users:send_invite")
            response = admin_api_client.post(url, default_invitation_data)

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

    @pytest.mark.django_db
    def test_email_error(self, admin_api_client, default_invitation_data):
        with mock.patch.multiple(
            "dook.core.users.models", send_registration_invitation_email=mock.DEFAULT
        ) as mocked:
            mocked["send_registration_invitation_email"].return_value = False

            url = reverse(f"users:send_invite")
            response = admin_api_client.post(url, default_invitation_data)

            invitation = Invitation.objects.filter(
                email=default_invitation_data["email"]
            ).first()

            assert response.status_code == 503

            assert_that(invitation).is_none()
            assert_that(response.data["detail"].code).is_equal_to(
                InternalEmailErrorException.default_code
            )

    @pytest.mark.django_db
    def test_without_permissions(self, api_client, default_invitation_data):
        url = reverse(f"users:send_invite")
        response = api_client.post(url, default_invitation_data)

        assert response.status_code == 401


class TestPasswordResetRequestView:
    @pytest.mark.django_db
    def test_success_request(self, api_client):
        with mock.patch.multiple(
            "dook.api.users.views", send_password_reset_email=mock.DEFAULT
        ) as mocked:
            mocked["send_password_reset_email"].return_value = True
            user = UserFactory(email="test@dook.pro")

            url = reverse(f"users:password_reset_request")
            response = api_client.post(url, {"email": user.email}, format="json")

            assert response.status_code == 200

            reset_url = password_reset_token_generator.make_url(user)

            assert mocked["send_password_reset_email"].called
            assert mocked["send_password_reset_email"].with_args(user.email, reset_url)

    @pytest.mark.django_db
    def test_request_invalid_email(self, api_client):
        with mock.patch.multiple(
            "dook.api.users.views", send_password_reset_email=mock.DEFAULT
        ) as mocked:
            url = reverse(f"users:password_reset_request")
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
            f"users:password_reset",
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
            f"users:password_reset",
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
            f"users:password_reset",
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
            f"users:password_reset",
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
        url = reverse("users:internal_password_reset",)
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
        url = reverse("users:internal_password_reset",)
        new_password = "Password54321!"
        data = {
            "old_password": "wrongpassword",
            "password": new_password,
            "password2": new_password,
        }
        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == 400
        assert_that(default_user.check_password(new_password)).is_false()


class TestUserDetailView:
    @pytest.mark.django_db
    def test_success(self, authenticated_api_client, default_user):
        response = authenticated_api_client.get(reverse("users:current_user"))

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "email": default_user.email,
            "name": default_user.name,
            "role": default_user.role,
        }

    @pytest.mark.django_db
    def test_wrong_credentials(self, api_client):
        response = api_client.get(
            reverse("users:current_user"), HTTP_AUTHORIZATION=str(uuid4()),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
