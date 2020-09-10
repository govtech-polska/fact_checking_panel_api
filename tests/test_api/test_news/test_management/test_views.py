import tempfile
from datetime import datetime
from unittest import mock
from uuid import uuid4

import pytest
from assertpy import assert_that
from django.urls import reverse
from PIL import Image
from rest_framework import status

from dook.api.news.consts import MAX_TAG_COUNT_PER_NEWS, OpinionType
from dook.api.news.exceptions import (
    MissingFieldsException,
    TagCountPerNewsExceededException,
)
from dook.api.news.management.exceptions import (
    AssigningNewsToInactiveUserException,
    NewsAlreadyAssignedException,
    NewsAlreadyAssignedToRequestedUserException,
)
from dook.core.news.constants import NewsOrigin, VerdictType
from dook.core.news.models import News, NewsTag, Tag
from dook.core.users.constants import UserRoleType
from dook.core.users.models import UserNews
from tests.factories.news import (
    DomainFactory,
    ExpertOpinionFactory,
    FactCheckerOpinionFactory,
    NewsDomainFactory,
    NewsFactory,
    NewsTagFactory,
    TagFactory,
)
from tests.factories.users import UserFactory, UserNewsFactory


@pytest.fixture
def default_opinion_data():
    return {
        "title": "Some random title",
        "confirmation_sources": "drop.com",
        "verdict": VerdictType.VERIFIED_TRUE,
        "comment": "Thinking through all the facts and other dependencies, yes.",
        "is_duplicate": False,
        "duplicate_reference": None,
    }


@pytest.fixture
def test_opinion_update_payload():
    def _test_verdict_update_payload(
        opinion_type=OpinionType.VERDICT.value, verdict=VerdictType.VERIFIED_TRUE
    ):
        if opinion_type == OpinionType.VERDICT.value:
            return {
                "comment": "test_update_comment",
                "confirmation_sources": "test_confirmation_sources",
                "title": "test_update_title",
                "verdict": verdict,
                "type": opinion_type,
            }
        elif opinion_type == OpinionType.SPAM.value:
            return {"verdict": VerdictType.SPAM, "type": opinion_type}
        else:
            return {
                "is_duplicate": True,
                "duplicate_reference": uuid4(),
                "type": OpinionType.DUPLICATE.value,
            }

    return _test_verdict_update_payload


@pytest.mark.django_db
class TestNewsViewSet:
    list_url = reverse("news:management:news")

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR),
    )
    def test_list(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        NewsFactory.create_batch(2)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_with_domains(self, admin_api_client):
        news = NewsFactory()
        domains = DomainFactory.create_batch(2)
        [NewsDomainFactory(news=news, domain=domain) for domain in domains]

        response = admin_api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"][0]["domains"]) == 2

    def test_list_group_by_is_pinned(self, admin_api_client):
        NewsFactory.create_batch(2, is_pinned=True)
        not_pinned = NewsFactory(is_pinned=False)

        response = admin_api_client.get(self.list_url, data={"is_pinned": False})

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["results"]) == 1
        assert response_data["results"][0]["id"] == str(not_pinned.id)

    def test_list_filter_by_tags(self, admin_api_client):
        tag_1, tag_2 = TagFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)

        NewsTagFactory(news=news_1, tag=tag_1)
        NewsTagFactory(news=news_2, tag=tag_2)
        NewsTagFactory(news=news_3, tag=tag_1)
        NewsTagFactory(news=news_3, tag=tag_2)
        NewsTagFactory(news=news_4, tag=tag_1)

        response = admin_api_client.get(
            self.list_url, data={"tags[]": [tag_1.name, tag_2.name]}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

        response = admin_api_client.get(self.list_url, data={"tags[]": [tag_1.name]})
        assert len(response.json()["results"]) == 3

        response = admin_api_client.get(self.list_url, data={"tags[]": [tag_2.name]})
        assert len(response.json()["results"]) == 2

        response = admin_api_client.get(
            self.list_url, data={"tags[]": [TagFactory().name]}
        )
        assert len(response.json()["results"]) == 0

        response = admin_api_client.get(self.list_url, data={"tags[]": [uuid4()]})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_filter_by_domains(self, admin_api_client):
        domain_1, domain_2 = DomainFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)

        NewsDomainFactory(news=news_1, domain=domain_1)
        NewsDomainFactory(news=news_2, domain=domain_2)
        NewsDomainFactory(news=news_3, domain=domain_1)
        NewsDomainFactory(news=news_3, domain=domain_2)
        NewsDomainFactory(news=news_4, domain=domain_1)

        response = admin_api_client.get(
            self.list_url, data={"domains[]": [domain_1.name, domain_2.name]}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

        response = admin_api_client.get(
            self.list_url, data={"domains[]": [domain_1.name]}
        )
        assert len(response.json()["results"]) == 3

        response = admin_api_client.get(
            self.list_url, data={"domains[]": [domain_2.name]}
        )
        assert len(response.json()["results"]) == 2

        response = admin_api_client.get(
            self.list_url, data={"domains[]": [DomainFactory().name]}
        )
        assert len(response.json()["results"]) == 0

        response = admin_api_client.get(self.list_url, data={"domains[]": [uuid4()]})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_list_filter_by_verified_news(self, admin_api_client):
        assert News.objects.count() == 0

        news_1, _, _ = NewsFactory.create_batch(3)
        user = UserFactory(role=UserRoleType.EXPERT)
        ExpertOpinionFactory(news=news_1, judge=user)

        response = admin_api_client.get(
            self.list_url, data={"is_verified_by_expert": False}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert str(news_1.id) not in [item["id"] for item in response.json()["results"]]

        response = admin_api_client.get(
            self.list_url, data={"is_verified_by_expert": True}
        )

        assert len(response.data["results"]) == 1
        assert response.json()["results"][0]["id"] == str(news_1.id)

    def test_list_filter_by_origin(self, admin_api_client):
        news_plugin = NewsFactory(origin=NewsOrigin.PLUGIN)
        news_chatbot = NewsFactory(origin=NewsOrigin.CHATBOT)
        news_mobile = NewsFactory(origin=NewsOrigin.MOBILE)

        for news in (news_plugin, news_chatbot, news_mobile):
            response = admin_api_client.get(self.list_url, data={"origin": news.origin})

            response_data = response.json()
            assert len(response_data["results"]) == 1
            assert response_data["results"][0]["id"] == str(news.id)

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR),
    )
    def test_detail(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        news = NewsFactory()
        domain = DomainFactory()
        NewsDomainFactory(news=news, domain=domain)

        response = api_client.get(
            reverse(f"news:management:news", kwargs={"pk": news.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.id)
        assert response.data["domains"][0]["id"] == str(domain.id)

    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR),
    )
    def test_update(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        news = NewsFactory(is_pinned=False, is_published=False)
        new_text = "Wearing a foil hat, protects against coronavirus."
        data = {"text": new_text, "is_pinned": True, "is_published": True}

        url = reverse(f"news:management:news", kwargs={"pk": news.id})
        response = api_client.patch(url, data, format="json")
        news.refresh_from_db()

        assert response.status_code == 200
        assert_that(news.text).is_equal_to(new_text)
        assert news.is_pinned is True
        assert news.is_published is True

    def test_update_domains(self, admin_api_client):
        news = NewsFactory()
        domain = DomainFactory()
        NewsDomainFactory(news=news, domain=DomainFactory())
        payload = {"domains": [domain.pk, domain.pk]}

        url = reverse(f"news:management:news", kwargs={"pk": news.id})
        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == 200
        assert len(response.data["domains"]) == 1
        assert response.data["domains"][0]["id"] == str(domain.id)

        payload = {"domains": [uuid4()]}
        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_tags(self, admin_api_client):
        news = NewsFactory()
        tags = TagFactory.create_batch(2)
        NewsTagFactory(news=news, tag=tags[0])
        new_tag_name = "new_tag_name"

        assert Tag.objects.count() == 2
        assert NewsTag.objects.count() == 1

        payload = {"tags": [tags[0].name, tags[1].name, new_tag_name]}

        url = reverse(f"news:management:news", kwargs={"pk": news.id})
        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == 200
        assert len(response.json()["tags"]) == 3
        assert Tag.objects.count() == 3
        assert NewsTag.objects.count() == 3

        payload = {"tags": [f"{i}" for i in range(MAX_TAG_COUNT_PER_NEWS + 1)]}
        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code == TagCountPerNewsExceededException.default_code
        )


@pytest.mark.django_db
class TestExpertOpinionDetailView:
    @staticmethod
    def _detail_url(pk):
        return reverse("news:management:expert-opinion-detail", kwargs={"pk": pk})

    @pytest.mark.parametrize(
        "role, expected_status",
        (
            (UserRoleType.ADMIN, status.HTTP_200_OK),
            (UserRoleType.MODERATOR, status.HTTP_200_OK),
            (UserRoleType.EXPERT, status.HTTP_200_OK),
            (UserRoleType.SPECIALIST, status.HTTP_200_OK),
            (UserRoleType.FACT_CHECKER, status.HTTP_403_FORBIDDEN),
        ),
    )
    def test_check_authorization(
        self,
        api_client,
        default_opinion_data,
        test_opinion_update_payload,
        role,
        expected_status,
    ):
        api_client.force_authenticate(user=UserFactory(role=role))

        opinion = ExpertOpinionFactory(**default_opinion_data)

        response = api_client.put(
            self._detail_url(pk=opinion.id), data=test_opinion_update_payload()
        )

        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "opinion_type, missing_field, expected_status",
        (
            (OpinionType.VERDICT.value, None, status.HTTP_200_OK),
            (OpinionType.VERDICT.value, "title", status.HTTP_400_BAD_REQUEST),
            (OpinionType.VERDICT.value, "comment", status.HTTP_400_BAD_REQUEST),
            (
                OpinionType.VERDICT.value,
                "confirmation_sources",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.VERDICT.value, "verdict", status.HTTP_400_BAD_REQUEST),
            (OpinionType.DUPLICATE.value, None, status.HTTP_200_OK),
            (
                OpinionType.DUPLICATE.value,
                "duplicate_reference",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.SPAM.value, None, status.HTTP_200_OK),
        ),
    )
    def test_update_verdict(
        self,
        admin_api_client,
        default_opinion_data,
        test_opinion_update_payload,
        opinion_type,
        missing_field,
        expected_status,
    ):
        opinion = ExpertOpinionFactory(**default_opinion_data)

        payload = {
            k: v
            for k, v in test_opinion_update_payload(opinion_type=opinion_type).items()
            if k != missing_field
        }

        response = admin_api_client.put(self._detail_url(pk=opinion.id), data=payload)

        assert response.status_code == expected_status
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            assert (
                response.json()["detail"]
                == MissingFieldsException(missing_fields=(missing_field,)).detail
            )
        elif response.status_code == status.HTTP_200_OK:
            if opinion_type == OpinionType.VERDICT.value:
                opinion.refresh_from_db()
                assert opinion.comment == payload["comment"]
                assert opinion.confirmation_sources == payload["confirmation_sources"]
                assert opinion.verdict == payload["verdict"]
                assert opinion.title == payload["title"]
                assert opinion.is_duplicate is False
                assert opinion.duplicate_reference is None
            elif opinion_type == OpinionType.DUPLICATE.value:
                opinion.refresh_from_db()
                assert opinion.comment == ""
                assert opinion.confirmation_sources == ""
                assert opinion.verdict == ""
                assert opinion.title == ""
                assert opinion.is_duplicate is True
                assert opinion.duplicate_reference == payload["duplicate_reference"]
            elif opinion_type == OpinionType.SPAM.value:
                opinion.refresh_from_db()
                assert opinion.comment == ""
                assert opinion.confirmation_sources == ""
                assert opinion.verdict == VerdictType.SPAM
                assert opinion.title == ""
                assert opinion.is_duplicate is False
                assert opinion.duplicate_reference is None


@pytest.mark.django_db
class TestFactCheckerOpinionDetailView:
    @staticmethod
    def _detail_url(pk):
        return reverse("news:management:fact-checker-opinion-detail", kwargs={"pk": pk})

    @pytest.mark.parametrize(
        "role, expected_status",
        (
            (UserRoleType.ADMIN, status.HTTP_200_OK),
            (UserRoleType.MODERATOR, status.HTTP_200_OK),
            (UserRoleType.EXPERT, status.HTTP_403_FORBIDDEN),
            (UserRoleType.SPECIALIST, status.HTTP_403_FORBIDDEN),
            (UserRoleType.FACT_CHECKER, status.HTTP_403_FORBIDDEN),
        ),
    )
    def test_check_authorization(
        self,
        api_client,
        default_opinion_data,
        test_opinion_update_payload,
        role,
        expected_status,
    ):
        api_client.force_authenticate(user=UserFactory(role=role))

        opinion = FactCheckerOpinionFactory(**default_opinion_data)

        response = api_client.put(
            self._detail_url(pk=opinion.id), data=test_opinion_update_payload()
        )

        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "opinion_type, missing_field, expected_status",
        (
            (OpinionType.VERDICT.value, None, status.HTTP_200_OK),
            (OpinionType.VERDICT.value, "title", status.HTTP_400_BAD_REQUEST),
            (OpinionType.VERDICT.value, "comment", status.HTTP_400_BAD_REQUEST),
            (
                OpinionType.VERDICT.value,
                "confirmation_sources",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.VERDICT.value, "verdict", status.HTTP_400_BAD_REQUEST),
            (OpinionType.DUPLICATE.value, None, status.HTTP_200_OK),
            (
                OpinionType.DUPLICATE.value,
                "duplicate_reference",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.SPAM.value, None, status.HTTP_200_OK),
        ),
    )
    def test_update_verdict(
        self,
        admin_api_client,
        default_opinion_data,
        test_opinion_update_payload,
        opinion_type,
        missing_field,
        expected_status,
    ):
        opinion = FactCheckerOpinionFactory(**default_opinion_data)

        payload = {
            k: v
            for k, v in test_opinion_update_payload(opinion_type=opinion_type).items()
            if k != missing_field
        }

        response = admin_api_client.put(self._detail_url(pk=opinion.id), data=payload)

        assert response.status_code == expected_status
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            assert (
                response.json()["detail"]
                == MissingFieldsException(missing_fields=(missing_field,)).detail
            )
        elif response.status_code == status.HTTP_200_OK:
            if opinion_type == OpinionType.VERDICT.value:
                opinion.refresh_from_db()
                assert opinion.comment == payload["comment"]
                assert opinion.confirmation_sources == payload["confirmation_sources"]
                assert opinion.verdict == payload["verdict"]
                assert opinion.title == payload["title"]
                assert opinion.is_duplicate is False
                assert opinion.duplicate_reference is None
            elif opinion_type == OpinionType.DUPLICATE.value:
                opinion.refresh_from_db()
                assert opinion.comment == ""
                assert opinion.confirmation_sources == ""
                assert opinion.verdict == ""
                assert opinion.title == ""
                assert opinion.is_duplicate is True
                assert opinion.duplicate_reference == payload["duplicate_reference"]
            elif opinion_type == OpinionType.SPAM.value:
                opinion.refresh_from_db()
                assert opinion.comment == ""
                assert opinion.confirmation_sources == ""
                assert opinion.verdict == VerdictType.SPAM
                assert opinion.title == ""
                assert opinion.is_duplicate is False
                assert opinion.duplicate_reference is None


class TestNewsImageView:
    @pytest.fixture
    def image_file(self):
        image = Image.new("RGB", (100, 100))

        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file)

        tmp_file.seek(0)
        return tmp_file

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR),
    )
    def test_upload_image(self, api_client, image_file, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        with mock.patch.multiple(
            "dook.core.integrations.storage.client.S3ApiClient",
            upload_image=mock.DEFAULT,
            get_object_url=mock.DEFAULT,
            generate_filename=mock.DEFAULT,
        ) as mocked:
            filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            image_url = "https://bucket_name.s3.amazonaws.com/{filename}"

            mocked["upload_image"].return_value = True
            mocked["generate_filename"].return_value = filename
            mocked["get_object_url"].return_value = image_url

            news = NewsFactory()
            url = reverse(f"news:management:news-image", kwargs={"pk": news.id})

            response = api_client.patch(url, {"image": image_file}, format="multipart")
            news.refresh_from_db()

            assert response.status_code == 204
            assert_that(news.screenshot_url).is_equal_to(image_url)


@pytest.mark.django_db
class TestNewsAssignView:
    @pytest.mark.parametrize(
        "assignee_role", (UserRoleType.EXPERT, UserRoleType.SPECIALIST)
    )
    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_assign_news(self, api_client, assignee_role, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        with mock.patch(
            "dook.api.news.management.views.send_news_assignment_for_expert"
        ) as mocked:
            assert UserNews.objects.count() == 0

            news = NewsFactory()
            user = UserFactory(role=assignee_role)
            requesting_user = api_client.handler._force_user

            response = api_client.patch(
                reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
                data={"assignee": user.pk},
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert UserNews.objects.count() == 1

            user_news = UserNews.objects.first()
            assert user_news.assigned_by_email == requesting_user.email
            assert user_news.news == news
            assert user_news.user == user

            assert mocked.called
            assert mocked.call_args == mock.call(expert=user, news=news)

    @pytest.mark.parametrize(
        "role",
        (
            UserRoleType.ADMIN,
            UserRoleType.MODERATOR,
            UserRoleType.FACT_CHECKER,
            UserRoleType.BASE_USER,
        ),
    )
    def test_assign_to_non_expert_or_non_specialist(self, admin_api_client, role):
        news = NewsFactory()
        user = UserFactory(role=role)

        response = admin_api_client.patch(
            reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
            data={"assignee": user.pk},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["assignee"] == [
            f'Invalid pk "{user.pk}" - object does not exist.'
        ]

    def test_assign_already_assigned_news(self, admin_api_client):
        news = NewsFactory()
        user_1 = UserFactory(role=UserRoleType.EXPERT)
        user_2 = UserFactory(role=UserRoleType.SPECIALIST)
        UserNewsFactory(user=user_1, news=news)

        response = admin_api_client.patch(
            reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
            data={"assignee": user_2.pk},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"].code == NewsAlreadyAssignedException.default_code

        response = admin_api_client.patch(
            reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
            data={"assignee": user_1.pk},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code
            == NewsAlreadyAssignedToRequestedUserException.default_code
        )

        with mock.patch.multiple(
            "dook.api.news.management.views",
            send_news_assignment_for_expert=mock.DEFAULT,
            send_news_dismissal_for_expert=mock.DEFAULT,
        ) as mocked:
            response = admin_api_client.patch(
                reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
                data={"assignee": user_2.pk, "replace_assignee": True},
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert UserNews.objects.count() == 1
            assert UserNews.objects.first().user == user_2

            assert mocked["send_news_assignment_for_expert"].called
            assert mocked["send_news_dismissal_for_expert"].called
            assert mocked["send_news_assignment_for_expert"].call_args == mock.call(
                expert=user_2, news=news
            )
            assert mocked["send_news_dismissal_for_expert"].call_args == mock.call(
                expert=user_1, news=news
            )

    def test_assign_already_verified_news(self, admin_api_client):
        news = NewsFactory()
        user_1 = UserFactory(role=UserRoleType.EXPERT)
        UserNewsFactory(user=user_1, news=news)
        ExpertOpinionFactory(news=news, judge=user_1)

        response = admin_api_client.patch(
            reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
            data={
                "assignee": str(UserFactory(role=UserRoleType.SPECIALIST).pk),
                "replace_assignee": True,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_assign_to_inactive_user(self, admin_api_client):
        news = NewsFactory()

        response = admin_api_client.patch(
            reverse(f"news:management:news-assign", kwargs={"pk": str(news.id)}),
            data={
                "assignee": str(
                    UserFactory(role=UserRoleType.SPECIALIST, is_active=False).pk
                ),
                "replace_assignee": True,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code
            == AssigningNewsToInactiveUserException.default_code
        )


@pytest.mark.django_db
class TestNewsDismissView:
    @pytest.mark.parametrize(
        "role", (UserRoleType.ADMIN, UserRoleType.MODERATOR,),
    )
    def test_dismiss_news(self, api_client, role):
        api_client.force_authenticate(user=UserFactory(role=role))

        with mock.patch(
            "dook.api.news.management.views.send_news_dismissal_for_expert"
        ) as mocked:
            news = NewsFactory()
            user = UserFactory(role=UserRoleType.EXPERT)
            UserNewsFactory(news=news, user=user)

            response = api_client.delete(
                reverse(
                    f"news:management:news-dismiss-assignment",
                    kwargs={"pk": str(news.id)},
                ),
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT

            assert mocked.called
            assert mocked.call_args == mock.call(expert=user, news=news)
