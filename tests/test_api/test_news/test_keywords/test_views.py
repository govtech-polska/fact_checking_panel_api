import pytest
from django.urls import reverse
from rest_framework import status

from dook.api.news.keywords.exceptions import (
    DomainAssignedToUserInvitationOnDeleteException,
    DomainAssignedToUserOnDeleteException,
)
from dook.core.news.models import (
    Domain,
    NewsDomain,
    NewsSensitiveKeyword,
    NewsTag,
    SensitiveKeyword,
    Tag,
)
from dook.core.users.constants import InvitationStatusType, UserRoleType
from tests.factories.news import (
    DomainFactory,
    NewsDomainFactory,
    NewsFactory,
    NewsSensitiveKeywordFactory,
    NewsTagFactory,
    SensitiveKeywordFactory,
    TagFactory,
)
from tests.factories.users import InvitationFactory, UserFactory


@pytest.mark.django_db
class TestSensitiveKeywordViewSet:
    list_url = reverse("news:keywords:sensitive-keywords")

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_list(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        assert SensitiveKeyword.objects.count() == 0
        SensitiveKeywordFactory.create_batch(2)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_search(self, admin_api_client):
        assert SensitiveKeyword.objects.count() == 0
        keyword = SensitiveKeywordFactory(name="123")
        SensitiveKeywordFactory.create_batch(2)

        response = admin_api_client.get(self.list_url, data={"search": keyword.name})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == keyword.name

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_create(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        assert SensitiveKeyword.objects.count() == 0

        payload = {"name": "test_name"}
        response = api_client.post(self.list_url, data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == payload["name"]
        assert SensitiveKeyword.objects.count() == 1

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_detail(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        keyword = SensitiveKeywordFactory()

        response = api_client.get(
            reverse("news:keywords:sensitive-keywords", kwargs={"pk": keyword.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(keyword.pk)

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_update(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        keyword = SensitiveKeywordFactory()
        payload = {"name": f"{keyword.name}_1"}

        response = api_client.patch(
            reverse("news:keywords:sensitive-keywords", kwargs={"pk": keyword.pk}),
            data=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == payload["name"]
        assert SensitiveKeyword.objects.get(pk=keyword.pk).name == payload["name"]

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_delete(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        keyword = SensitiveKeywordFactory()
        NewsSensitiveKeywordFactory(sensitive_keyword=keyword, news=NewsFactory())

        response = api_client.delete(
            reverse("news:keywords:sensitive-keywords", kwargs={"pk": keyword.pk})
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert SensitiveKeyword.objects.count() == 0
        assert NewsSensitiveKeyword.objects.count() == 0


@pytest.mark.django_db
class TestDomainViewSet:
    list_url = reverse("news:keywords:domains")

    def test_list(self, api_client):
        assert Domain.objects.count() == 0
        DomainFactory.create_batch(2)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_search(self, api_client):
        assert Domain.objects.count() == 0
        domain = DomainFactory(name="123")
        DomainFactory.create_batch(2)

        response = api_client.get(self.list_url, data={"search": domain.name})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == domain.name

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_create(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        assert Domain.objects.count() == 0

        payload = {"name": "test_name"}
        response = api_client.post(self.list_url, data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == payload["name"]
        assert Domain.objects.count() == 1

    @pytest.mark.parametrize(
        "role",
        (
            UserRoleType.ADMIN,
            UserRoleType.MODERATOR,
            UserRoleType.EXPERT,
            UserRoleType.SPECIALIST,
            UserRoleType.FACT_CHECKER,
        ),
    )
    def test_detail(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        domain = DomainFactory()

        response = api_client.get(
            reverse("news:keywords:domains", kwargs={"pk": domain.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(domain.pk)

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_update(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        domain = DomainFactory()
        payload = {"name": f"{domain.name}_1"}

        response = api_client.patch(
            reverse("news:keywords:domains", kwargs={"pk": domain.pk}), data=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == payload["name"]
        assert Domain.objects.get(pk=domain.pk).name == payload["name"]

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_delete(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))
        domain = DomainFactory()
        NewsDomainFactory(domain=domain, news=NewsFactory())

        response = api_client.delete(
            reverse("news:keywords:domains", kwargs={"pk": domain.pk})
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Domain.objects.count() == 0
        assert NewsDomain.objects.count() == 0

    def test_delete_assigned_to_user(self, admin_api_client):
        domain = DomainFactory()
        UserFactory(domain=domain)

        response = admin_api_client.delete(
            reverse("news:keywords:domains", kwargs={"pk": domain.pk})
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code
            == DomainAssignedToUserOnDeleteException.default_code
        )

    def test_delete_assigned_to_user_invitation(self, admin_api_client):
        domain = DomainFactory()
        InvitationFactory(domain=domain, status=InvitationStatusType.WAITING)

        response = admin_api_client.delete(
            reverse("news:keywords:domains", kwargs={"pk": domain.pk})
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code
            == DomainAssignedToUserInvitationOnDeleteException.default_code
        )


@pytest.mark.django_db
class TestTagViewSet:
    list_url = reverse("news:keywords:tags")

    def test_list(self, api_client):
        assert Tag.objects.count() == 0
        TagFactory.create_batch(2)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_search(self, api_client):
        assert Tag.objects.count() == 0
        tag = TagFactory(name="123")
        TagFactory.create_batch(2)

        response = api_client.get(self.list_url, data={"search": tag.name})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == tag.name

    def test_list_sort_by_popularity(self, api_client):
        assert Tag.objects.count() == 0
        tag_1, tag_2, tag_3 = TagFactory.create_batch(3)
        [NewsTagFactory(news=NewsFactory(), tag=tag_3) for _ in range(3)]
        [NewsTagFactory(news=NewsFactory(), tag=tag_1) for _ in range(2)]
        NewsTagFactory(news=NewsFactory(), tag=tag_2)

        response = api_client.get(self.list_url, data={"popular": True})

        assert response.status_code == status.HTTP_200_OK
        response_list = response.json()["results"]
        assert response_list[0]["id"] == str(tag_3.id)
        assert response_list[1]["id"] == str(tag_1.id)
        assert response_list[2]["id"] == str(tag_2.id)

    @pytest.mark.parametrize(
        "role",
        (
            UserRoleType.ADMIN,
            UserRoleType.MODERATOR,
            UserRoleType.EXPERT,
            UserRoleType.SPECIALIST,
        ),
    )
    def test_create(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        assert Tag.objects.count() == 0

        payload = {"name": "test_name"}
        response = api_client.post(self.list_url, data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == payload["name"]
        assert Tag.objects.count() == 1

    @pytest.mark.parametrize(
        "role",
        (
            UserRoleType.ADMIN,
            UserRoleType.MODERATOR,
            UserRoleType.EXPERT,
            UserRoleType.SPECIALIST,
            UserRoleType.FACT_CHECKER,
        ),
    )
    def test_detail(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        tag = TagFactory()

        response = api_client.get(reverse("news:keywords:tags", kwargs={"pk": tag.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(tag.pk)

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_update(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        tag = TagFactory()
        payload = {"name": f"{tag.name}_1"}

        response = api_client.patch(
            reverse("news:keywords:tags", kwargs={"pk": tag.pk}), data=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == payload["name"]
        assert Tag.objects.get(pk=tag.pk).name == payload["name"]

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_delete(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        tag = TagFactory()
        NewsTagFactory(tag=tag, news=NewsFactory())

        response = api_client.delete(reverse("news:keywords:tags", kwargs={"pk": tag.pk}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Tag.objects.count() == 0
        assert NewsTag.objects.count() == 0
