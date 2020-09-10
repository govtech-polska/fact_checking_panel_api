from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

from dook.api.users.exceptions import (
    DomainAssignToNonSpecialistRoleException,
    MissingDomainForSpecialistRoleException,
    UpdatingRoleNotDedicatedForPromotionException,
)
from dook.core.users.constants import (
    InvitationStatusType,
    UserRoleType,
    UserSpecializationType,
)
from dook.core.users.models import Invitation, User, UserNews
from tests.factories.news import (
    DomainFactory,
    ExpertOpinionFactory,
    FactCheckerOpinionFactory,
    NewsFactory,
)
from tests.factories.users import InvitationFactory, UserFactory, UserNewsFactory


@pytest.mark.django_db
class TestCurrentUserView:
    url = reverse("users:current-user")

    def test_success(self, authenticated_api_client, default_user):
        response = authenticated_api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "email": default_user.email,
            "name": default_user.name,
            "role": default_user.role,
            "allow_subscriptions": default_user.allow_subscriptions,
        }

    def test_wrong_credentials(self, api_client):
        response = api_client.get(self.url, HTTP_AUTHORIZATION=str(uuid4()))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserDetailView:
    def test_detail(self, admin_api_client):
        user = UserFactory()

        response = admin_api_client.get(
            reverse("users:user-detail", kwargs={"pk": user.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == user.role
        assert response.data["is_active"] == user.is_active
        assert response.data["name"] == user.name
        assert response.data["specialization"] == user.specialization

    def test_update(self, admin_api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER, is_active=True)
        payload = {
            "is_active": False,
            "name": f"{user.name}_test",
            "specialization": UserSpecializationType.BIOLOGY,
        }

        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": user.pk}), data=payload
        )

        user = User.objects.get(pk=user.pk)
        assert response.data["is_active"] == payload["is_active"]
        assert user.is_active == payload["is_active"]
        assert response.data["name"] == user.name
        assert response.data["specialization"] == user.specialization

    def test_update_domain(self, admin_api_client):
        user = UserFactory(role=UserRoleType.SPECIALIST, domain=DomainFactory())
        domain = DomainFactory()
        payload = {"domain": domain.pk}

        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": user.pk}), data=payload
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["domain"]["name"] == domain.name

        user = UserFactory(role=UserRoleType.EXPERT, domain=DomainFactory())

        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": user.pk}), data=payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code
            == DomainAssignToNonSpecialistRoleException.default_code
        )

    def test_update_role(self, admin_api_client):
        admin = UserFactory(role=UserRoleType.ADMIN)
        moderator = UserFactory(role=UserRoleType.MODERATOR)
        expert = UserFactory(role=UserRoleType.EXPERT)
        specialist = UserFactory(role=UserRoleType.SPECIALIST)
        fact_checker = UserFactory(role=UserRoleType.FACT_CHECKER)

        for user in (admin, fact_checker):
            response = admin_api_client.patch(
                reverse("users:user-detail", kwargs={"pk": user.pk}),
                data={"role": UserRoleType.EXPERT},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                response.data["detail"].code
                == UpdatingRoleNotDedicatedForPromotionException.default_code
            )

        for role in (UserRoleType.ADMIN, UserRoleType.FACT_CHECKER):
            response = admin_api_client.patch(
                reverse("users:user-detail", kwargs={"pk": expert.pk}),
                data={"role": role},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                response.data["detail"].code
                == UpdatingRoleNotDedicatedForPromotionException.default_code
            )

        # raise exception when promoting to specialist without provided domain
        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": expert.pk}),
            data={"role": UserRoleType.SPECIALIST},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code
            == MissingDomainForSpecialistRoleException.default_code
        )

        # delete assigned news when promoting to moderator
        UserNewsFactory(user=expert, news=NewsFactory())

        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": expert.pk}),
            data={"role": UserRoleType.MODERATOR},
        )

        assert response.status_code == status.HTTP_200_OK
        expert.refresh_from_db()
        assert expert.role == UserRoleType.MODERATOR
        assert UserNews.objects.count() == 0

        # reset user domain when promoting from specialist role to other
        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": specialist.pk}),
            data={"role": UserRoleType.MODERATOR},
        )

        assert response.status_code == status.HTTP_200_OK
        specialist.refresh_from_db()
        assert specialist.role == UserRoleType.MODERATOR
        assert specialist.domain is None

        domain = DomainFactory()
        response = admin_api_client.patch(
            reverse("users:user-detail", kwargs={"pk": moderator.pk}),
            data={"role": UserRoleType.SPECIALIST, "domain": domain.pk},
        )

        assert response.status_code == status.HTTP_200_OK
        moderator.refresh_from_db()
        assert moderator.role == UserRoleType.SPECIALIST
        assert moderator.domain.pk == domain.pk


@pytest.mark.django_db
class TestModeratorListView:
    url = reverse("users:moderator-list")

    def test_list(self, admin_api_client):
        UserFactory.create_batch(2, role=UserRoleType.MODERATOR)
        UserFactory(role=UserRoleType.FACT_CHECKER)

        response = admin_api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_order_by_verified_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(3, role=UserRoleType.MODERATOR)
        [
            ExpertOpinionFactory(news=news, judge=user_1)
            for news in NewsFactory.create_batch(2)
        ]
        [
            ExpertOpinionFactory(news=news, judge=user_2)
            for news in NewsFactory.create_batch(3)
        ]
        ExpertOpinionFactory(news=NewsFactory(), judge=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)


@pytest.mark.django_db
class TestExpertListView:
    url = reverse("users:expert-list")

    @pytest.mark.parametrize("role", (UserRoleType.ADMIN, UserRoleType.MODERATOR))
    def test_list(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        UserFactory.create_batch(2, role=UserRoleType.EXPERT)
        UserFactory(role=UserRoleType.FACT_CHECKER)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_order_by_assigned_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(3, role=UserRoleType.EXPERT)
        [UserNewsFactory(news=news, user=user_1) for news in NewsFactory.create_batch(2)]
        [UserNewsFactory(news=news, user=user_2) for news in NewsFactory.create_batch(3)]
        UserNewsFactory(news=NewsFactory(), user=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "assigned"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-assigned"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)

    def test_list_order_by_verified_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(3, role=UserRoleType.EXPERT)
        [
            ExpertOpinionFactory(news=news, judge=user_1)
            for news in NewsFactory.create_batch(2)
        ]
        [
            ExpertOpinionFactory(news=news, judge=user_2)
            for news in NewsFactory.create_batch(3)
        ]
        ExpertOpinionFactory(news=NewsFactory(), judge=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)


@pytest.mark.django_db
class TestSpecialistListView:
    url = reverse("users:specialist-list")

    @pytest.mark.parametrize("role", (UserRoleType.ADMIN, UserRoleType.MODERATOR))
    def test_list(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        UserFactory.create_batch(2, role=UserRoleType.SPECIALIST, domain=DomainFactory())
        UserFactory(role=UserRoleType.EXPERT)
        UserFactory(role=UserRoleType.FACT_CHECKER)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        domain = DomainFactory()
        UserFactory.create(role=UserRoleType.SPECIALIST, domain=domain)

        response = api_client.get(
            reverse("users:specialist-list"), data={"domain": domain.name}
        )

        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["domain"]["id"] == str(domain.id)

    def test_list_order_by_assigned_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(3, role=UserRoleType.SPECIALIST)
        [UserNewsFactory(news=news, user=user_1) for news in NewsFactory.create_batch(2)]
        [UserNewsFactory(news=news, user=user_2) for news in NewsFactory.create_batch(3)]
        UserNewsFactory(news=NewsFactory(), user=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "assigned"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-assigned"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)

    def test_list_order_by_verified_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(3, role=UserRoleType.SPECIALIST)
        [
            ExpertOpinionFactory(news=news, judge=user_1)
            for news in NewsFactory.create_batch(2)
        ]
        [
            ExpertOpinionFactory(news=news, judge=user_2)
            for news in NewsFactory.create_batch(3)
        ]
        ExpertOpinionFactory(news=NewsFactory(), judge=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)


@pytest.mark.django_db
class TestFactCheckerListView:
    url = reverse("users:fact-checker-list")

    def test_list(self, admin_api_client):
        UserFactory.create_batch(2, role=UserRoleType.FACT_CHECKER)
        UserFactory(role=UserRoleType.EXPERT)

        response = admin_api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_order_by_assigned_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(
            3, role=UserRoleType.FACT_CHECKER
        )
        [UserNewsFactory(news=news, user=user_1) for news in NewsFactory.create_batch(2)]
        [UserNewsFactory(news=news, user=user_2) for news in NewsFactory.create_batch(3)]
        UserNewsFactory(news=NewsFactory(), user=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "assigned"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-assigned"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)

    def test_list_order_by_verified_news(self, admin_api_client):
        user_1, user_2, user_3 = UserFactory.create_batch(
            3, role=UserRoleType.FACT_CHECKER
        )
        [
            FactCheckerOpinionFactory(news=news, judge=user_1)
            for news in NewsFactory.create_batch(2)
        ]
        [
            FactCheckerOpinionFactory(news=news, judge=user_2)
            for news in NewsFactory.create_batch(3)
        ]
        FactCheckerOpinionFactory(news=NewsFactory(), judge=user_3)

        response = admin_api_client.get(self.url, data={"ordering": "verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_3.id)
        assert response.data["results"][2]["id"] == str(user_2.id)

        response = admin_api_client.get(self.url, data={"ordering": "-verified"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == str(user_2.id)
        assert response.data["results"][2]["id"] == str(user_3.id)


@pytest.mark.django_db
class TestInvitationListView:
    url = reverse("users:invitation-list")

    def test_list(self, admin_api_client):
        InvitationFactory.create_batch(2)

        response = admin_api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_filter_by_status(self, admin_api_client):
        assert Invitation.objects.count() == 0

        InvitationFactory.create_batch(2, status=InvitationStatusType.IN_PROGRESS)
        used = InvitationFactory(status=InvitationStatusType.USED)

        response = admin_api_client.get(
            self.url, data={"status": InvitationStatusType.IN_PROGRESS}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert all(str(used.id) not in item["id"] for item in response.data["results"])

        response = admin_api_client.get(
            self.url, data={"status": InvitationStatusType.USED}
        )

        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(used.id)

    def test_list_filter_by_expired_invitations(self, admin_api_client):
        not_expired = InvitationFactory()
        expired_but_used = InvitationFactory(
            sent_at=datetime.utcnow().date()
            - timedelta(days=settings.INVITATION_EXPIRY + 1),
            status=InvitationStatusType.USED,
        )
        expired = InvitationFactory(
            sent_at=datetime.utcnow().date()
            - timedelta(days=settings.INVITATION_EXPIRY + 1)
        )

        response = admin_api_client.get(self.url, data={"is_expired": False})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert all(
            item["id"] in (str(not_expired.id), str(expired_but_used.id))
            for item in response.data["results"]
        )

        response = admin_api_client.get(self.url, data={"is_expired": True})

        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(expired.id)


@pytest.mark.django_db
class TestEditSubscriptionView:
    def test_list(self, api_client):
        user = UserFactory(allow_subscriptions=True)
        api_client.force_authenticate(user=user)

        response = api_client.patch(
            reverse("users:allow-subscriptions"), data={"allow_subscriptions": False},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.allow_subscriptions is False
