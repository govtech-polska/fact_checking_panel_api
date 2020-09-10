from unittest import mock
from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status

from dook.api.news.consts import MAX_TAG_COUNT_PER_NEWS, OpinionType
from dook.api.news.exceptions import (
    MissingFieldsException,
    TagCountPerNewsExceededException,
)
from dook.core.news.constants import NewsOrigin, VerdictType
from dook.core.news.models import ExpertOpinion, FactCheckerOpinion, News, NewsTag, Tag
from dook.core.users.constants import UserRoleType
from dook.core.users.models import UserNews
from tests.factories.news import (
    DomainFactory,
    ExpertOpinionFactory,
    NewsDomainFactory,
    NewsFactory,
    NewsTagFactory,
    TagFactory,
)
from tests.factories.users import UserFactory, UserNewsFactory


@pytest.fixture
def default_opinion_data():
    data = {
        "title": "Some random title",
        "confirmation_sources": "drop.com",
        "verdict": VerdictType.VERIFIED_TRUE,
        "comment": "Thinking through all the facts and other dependencies, yes.",
        "is_duplicate": False,
        "type": OpinionType.VERDICT.value,
    }
    return data


@pytest.fixture
def test_opinion_payload():
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
class TestExpertNewsViewSet:
    list_url = reverse("news:crew:expert-news")

    def test_list(self, api_client):
        NewsFactory.create_batch(2)
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_with_assigned_crew_member_email(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        news_1, news_2, _ = NewsFactory.create_batch(3)
        expert = UserFactory(role=UserRoleType.EXPERT)
        specialist = UserFactory(role=UserRoleType.SPECIALIST)
        UserNewsFactory(user=expert, news=news_1)
        UserNewsFactory(user=specialist, news=news_2)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK

        response_crew_member_emails = [
            item["assigned_crew_member"] for item in response.json()["results"]
        ]
        assert expert.email in response_crew_member_emails
        assert specialist.email in response_crew_member_emails
        assert None in response_crew_member_emails

    def test_list_with_tags_and_domains(self, api_client):
        assert News.objects.count() == 0

        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        news = NewsFactory()
        domain = DomainFactory()
        tag = TagFactory()
        NewsDomainFactory(news=news, domain=domain)
        NewsTagFactory(news=news, tag=tag)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()["results"][0]
        assert response_data["domains"][0]["id"] == str(domain.id)
        assert response_data["tags"][0]["id"] == str(tag.id)

    def test_list_filter_by_verified_news(self, api_client):
        assert News.objects.count() == 0

        news_1, _, _ = NewsFactory.create_batch(3)
        user = UserFactory(role=UserRoleType.EXPERT)
        ExpertOpinionFactory(news=news_1, judge=user)
        api_client.force_authenticate(user=user)

        response = api_client.get(self.list_url, data={"is_verified": False})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert str(news_1.id) not in [item["id"] for item in response.json()["results"]]

        response = api_client.get(self.list_url, data={"is_verified": True})

        assert len(response.data["results"]) == 1
        assert response.json()["results"][0]["id"] == str(news_1.id)

    def test_list_exclude_published_news(self, api_client):
        assert News.objects.count() == 0

        news = NewsFactory(is_published=False)
        user = UserFactory(role=UserRoleType.EXPERT)
        ExpertOpinionFactory(news=news, judge=user)
        api_client.force_authenticate(user=user)

        response = api_client.get(self.list_url)

        assert len(response.json()["results"]) == 1

        news.is_published = True
        news.save()

        response = api_client.get(self.list_url)

        assert len(response.json()["results"]) == 0

    def test_list_for_specialist_role(self, api_client):
        NewsFactory.create_batch(2)
        domain = DomainFactory()
        news = NewsFactory()
        NewsDomainFactory(news=news, domain=domain)

        user = UserFactory(role=UserRoleType.SPECIALIST, domain=domain)
        api_client.force_authenticate(user=user)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(news.id)

    def test_list_for_specialist_role_news_assigned_from_another_domain(self, api_client):
        domain = DomainFactory()
        user = UserFactory(role=UserRoleType.SPECIALIST, domain=domain)
        api_client.force_authenticate(user=user)

        news = NewsFactory()
        NewsDomainFactory(news=news, domain=DomainFactory())
        UserNewsFactory(news=news, user=user)

        response = api_client.get(self.list_url)

        assert len(response.data["results"]) == 1

    def test_list_filter_by_tags(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        tag_1, tag_2 = TagFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)

        NewsTagFactory(news=news_1, tag=tag_1)
        NewsTagFactory(news=news_2, tag=tag_2)
        NewsTagFactory(news=news_3, tag=tag_1)
        NewsTagFactory(news=news_3, tag=tag_2)
        NewsTagFactory(news=news_4, tag=tag_1)

        response = api_client.get(
            self.list_url, data={"tags[]": [tag_1.name, tag_2.name]}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

        response = api_client.get(self.list_url, data={"tags[]": [tag_1.name]})
        assert len(response.json()["results"]) == 3

        response = api_client.get(self.list_url, data={"tags[]": [tag_2.name]})
        assert len(response.json()["results"]) == 2

        response = api_client.get(self.list_url, data={"tags[]": [TagFactory().name]})
        assert len(response.json()["results"]) == 0

        response = api_client.get(self.list_url, data={"tags[]": [uuid4()]})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_filter_by_domains(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        domain_1, domain_2 = DomainFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)

        NewsDomainFactory(news=news_1, domain=domain_1)
        NewsDomainFactory(news=news_2, domain=domain_2)
        NewsDomainFactory(news=news_3, domain=domain_1)
        NewsDomainFactory(news=news_3, domain=domain_2)
        NewsDomainFactory(news=news_4, domain=domain_1)

        response = api_client.get(
            self.list_url, data={"domains[]": [domain_1.name, domain_2.name]}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

        response = api_client.get(self.list_url, data={"domains[]": [domain_1.name]})
        assert len(response.json()["results"]) == 3

        response = api_client.get(self.list_url, data={"domains[]": [domain_2.name]})
        assert len(response.json()["results"]) == 2

        response = api_client.get(
            self.list_url, data={"domains[]": [DomainFactory().name]}
        )
        assert len(response.json()["results"]) == 0

        response = api_client.get(self.list_url, data={"domains[]": [uuid4()]})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_filter_by_assignment(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        assigned_news = NewsFactory()
        UserNewsFactory(news=assigned_news, user=user)
        NewsFactory.create_batch(2)

        response = api_client.get(self.list_url, data={"assigned_to_me": True})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

        response = api_client.get(self.list_url, data={"assigned_to_me": False})

        assert len(response.json()["results"]) == 2

    def test_list_filter_by_origin(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        news_plugin = NewsFactory(origin=NewsOrigin.PLUGIN)
        news_chatbot = NewsFactory(origin=NewsOrigin.CHATBOT)
        news_mobile = NewsFactory(origin=NewsOrigin.MOBILE)

        for news in (news_plugin, news_chatbot, news_mobile):
            UserNewsFactory(news=news, user=user)

            response = api_client.get(self.list_url, data={"origin": news.origin})

            response_data = response.json()
            assert len(response_data["results"]) == 1
            assert response_data["results"][0]["id"] == str(news.id)

    def test_detail(self, api_client):
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        response = api_client.get(
            reverse("news:crew:expert-news", kwargs={"pk": news.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.pk)

        user = UserFactory(role=UserRoleType.SPECIALIST, domain=DomainFactory())
        api_client.force_authenticate(user=user)

        response = api_client.get(
            reverse("news:crew:expert-news", kwargs={"pk": news.pk})
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        news = NewsFactory()
        NewsDomainFactory(news=news, domain=user.domain)

        response = api_client.get(
            reverse("news:crew:expert-news", kwargs={"pk": news.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.pk)
        assert "domains" in response.data.keys()
        assert "tags" in response.data.keys()


@pytest.mark.django_db
class TestExpertNewsCreateOpinionView:
    @pytest.mark.parametrize(
        "role, expected_status",
        (
            (UserRoleType.ADMIN, status.HTTP_403_FORBIDDEN),
            (UserRoleType.MODERATOR, status.HTTP_201_CREATED),
            (UserRoleType.EXPERT, status.HTTP_201_CREATED),
            (UserRoleType.SPECIALIST, status.HTTP_201_CREATED),
            (UserRoleType.FACT_CHECKER, status.HTTP_403_FORBIDDEN),
        ),
    )
    def test_check_authorization(
        self, api_client, test_opinion_payload, role, expected_status,
    ):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ):
            with mock.patch("dook.core.integrations.chatbot.client.ApiClient"):
                news = NewsFactory()
                api_client.force_authenticate(user=UserFactory(role=role))

                response = api_client.post(
                    reverse(
                        "news:crew:expert-news-create-opinion", kwargs={"pk": news.pk}
                    ),
                    data=test_opinion_payload(),
                )

                assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "opinion_type, missing_field, expected_status",
        (
            (OpinionType.VERDICT.value, None, status.HTTP_201_CREATED),
            (OpinionType.VERDICT.value, "title", status.HTTP_400_BAD_REQUEST),
            (OpinionType.VERDICT.value, "comment", status.HTTP_400_BAD_REQUEST),
            (
                OpinionType.VERDICT.value,
                "confirmation_sources",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.VERDICT.value, "verdict", status.HTTP_400_BAD_REQUEST),
            (OpinionType.DUPLICATE.value, None, status.HTTP_201_CREATED),
            (
                OpinionType.DUPLICATE.value,
                "duplicate_reference",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.SPAM.value, None, status.HTTP_201_CREATED),
        ),
    )
    def test_create_opinion(
        self,
        api_client,
        test_opinion_payload,
        opinion_type,
        missing_field,
        expected_status,
    ):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ) as mocked:
            with mock.patch("dook.core.integrations.chatbot.client.ApiClient"):
                news = NewsFactory()
                user = UserFactory(role=UserRoleType.EXPERT)
                api_client.force_authenticate(user=user)

                payload = {
                    k: v
                    for k, v in test_opinion_payload(opinion_type=opinion_type).items()
                    if k != missing_field
                }
                url = reverse(
                    "news:crew:expert-news-create-opinion", kwargs={"pk": news.pk}
                )

                response = api_client.post(url, data=payload)

                assert response.status_code == expected_status
                response_data = response.json()
                if response.status_code == status.HTTP_400_BAD_REQUEST:
                    assert (
                        response.json()["detail"]
                        == MissingFieldsException(missing_fields=(missing_field,)).detail
                    )
                elif response.status_code == status.HTTP_201_CREATED:
                    expert_opinion = ExpertOpinion.objects.filter(
                        news=news, judge=user
                    ).first()
                    assert expert_opinion

                    if opinion_type == OpinionType.VERDICT.value:
                        email_args = {
                            "user_email": news.reporter_email,
                            "news_pk": news.pk,
                            "verdict_type": "VERIFIED_BY_EXPERT",
                        }

                        assert mocked["send_news_verified_notification"].called
                        assert mocked[
                            "send_news_verified_notification"
                        ].call_args == mock.call(**email_args)
                    else:
                        assert not mocked["send_news_verified_notification"].called

                    if opinion_type == OpinionType.VERDICT.value:
                        assert response_data["comment"] == payload["comment"]
                        assert (
                            response_data["confirmation_sources"]
                            == payload["confirmation_sources"]
                        )
                        assert response_data["verdict"] == payload["verdict"]
                        assert response_data["title"] == payload["title"]
                        assert response_data["is_duplicate"] is False
                        assert response_data["duplicate_reference"] is None
                    elif opinion_type == OpinionType.DUPLICATE.value:
                        assert response_data["comment"] == ""
                        assert response_data["confirmation_sources"] == ""
                        assert response_data["verdict"] == ""
                        assert response_data["title"] == ""
                        assert response_data["is_duplicate"] is True
                        assert response_data["duplicate_reference"] == str(
                            payload["duplicate_reference"]
                        )
                    elif opinion_type == OpinionType.SPAM.value:
                        assert response_data["comment"] == ""
                        assert response_data["confirmation_sources"] == ""
                        assert response_data["verdict"] == VerdictType.SPAM
                        assert response_data["title"] == ""
                        assert response_data["is_duplicate"] is False
                        assert response_data["duplicate_reference"] is None

    def test_already_opined(self, api_client, default_opinion_data):
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.EXPERT)
        ExpertOpinionFactory(news=news, judge=user)

        api_client.force_authenticate(user=user)

        url = reverse("news:crew:expert-news-create-opinion", kwargs={"pk": news.pk})
        response = api_client.post(url, default_opinion_data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestExpertNewsAssignTagsView:
    def test_assign_tags(self, api_client):
        assert Tag.objects.count() == 0
        assert NewsTag.objects.count() == 0

        news = NewsFactory()
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        url = reverse("news:crew:expert-news-assign-tags", kwargs={"pk": news.pk})
        payload = {"tags": ["tag_1", "tag_2"]}
        response = api_client.patch(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert Tag.objects.count() == 2
        assert NewsTag.objects.count() == 2
        assert sorted(payload["tags"]) == sorted(
            [item["name"] for item in response.json()["tags"]]
        )

        payload = {"tags": [f"{i}" for i in range(MAX_TAG_COUNT_PER_NEWS + 1)]}
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"].code == TagCountPerNewsExceededException.default_code
        )


@pytest.mark.django_db
class TestExpertNewsDismissAssignmentView:
    def test_dismiss_assignment(self, api_client):
        admin = UserFactory(role=UserRoleType.ADMIN)
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.EXPERT)
        UserNewsFactory(news=news, user=user, assigned_by_email="non@existing.email")

        assert UserNews.objects.count() == 1

        api_client.force_authenticate(user=user)

        with mock.patch(
            "dook.api.news.crew.views.send_news_assignment_rejection_for_assignor"
        ) as mocked:
            response = api_client.patch(
                reverse(
                    "news:crew:expert-news-dismiss-assignment", kwargs={"pk": news.pk}
                )
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert UserNews.objects.count() == 0

            assert not mocked.called

            UserNewsFactory(news=news, user=user, assigned_by_email=admin.email)
            response = api_client.patch(
                reverse(
                    "news:crew:expert-news-dismiss-assignment", kwargs={"pk": news.pk}
                )
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert UserNews.objects.count() == 0

            assert mocked.called
            assert mocked.call_args == mock.call(
                assignee=user, news=news, assignor_email=admin.email
            )


@pytest.mark.django_db
class TestFactCheckerNewsViewSet:
    list_url = reverse("news:crew:fact-checker-news")

    def test_list(self, api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        [UserNewsFactory(user=user, news=news) for news in NewsFactory.create_batch(2)]

        api_client.force_authenticate(user=user)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_list_filter_by_tags(self, api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        api_client.force_authenticate(user=user)

        tag_1, tag_2 = TagFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)
        [
            UserNewsFactory(user=user, news=news)
            for news in (news_1, news_2, news_3, news_4)
        ]

        NewsTagFactory(news=news_1, tag=tag_1)
        NewsTagFactory(news=news_2, tag=tag_2)
        NewsTagFactory(news=news_3, tag=tag_1)
        NewsTagFactory(news=news_3, tag=tag_2)
        NewsTagFactory(news=news_4, tag=tag_1)

        response = api_client.get(
            self.list_url, data={"tags[]": [tag_1.name, tag_2.name]}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

        response = api_client.get(self.list_url, data={"tags[]": [tag_1.name]})
        assert len(response.json()["results"]) == 3

        response = api_client.get(self.list_url, data={"tags[]": [tag_2.name]})
        assert len(response.json()["results"]) == 2

        response = api_client.get(self.list_url, data={"tags[]": [TagFactory().name]})
        assert len(response.json()["results"]) == 0

        response = api_client.get(self.list_url, data={"tags[]": [uuid4()]})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_filter_by_origin(self, api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        api_client.force_authenticate(user=user)

        news_plugin = NewsFactory(origin=NewsOrigin.PLUGIN)
        news_chatbot = NewsFactory(origin=NewsOrigin.CHATBOT)
        news_mobile = NewsFactory(origin=NewsOrigin.MOBILE)

        for news in (news_plugin, news_chatbot, news_mobile):
            UserNewsFactory(news=news, user=user)

            response = api_client.get(self.list_url, data={"origin": news.origin})

            response_data = response.json()
            assert len(response_data["results"]) == 1
            assert response_data["results"][0]["id"] == str(news.id)

    def test_detail(self, api_client):
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        UserNewsFactory(user=user, news=news)
        api_client.force_authenticate(user=user)

        response = api_client.get(
            reverse("news:crew:fact-checker-news", kwargs={"pk": news.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.pk)


@pytest.mark.django_db
class TestFactCheckerNewsCreateOpinionView:
    @pytest.mark.parametrize(
        "opinion_type, missing_field, expected_status",
        (
            (OpinionType.VERDICT.value, None, status.HTTP_201_CREATED),
            (OpinionType.VERDICT.value, "title", status.HTTP_400_BAD_REQUEST),
            (OpinionType.VERDICT.value, "comment", status.HTTP_400_BAD_REQUEST),
            (
                OpinionType.VERDICT.value,
                "confirmation_sources",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.VERDICT.value, "verdict", status.HTTP_400_BAD_REQUEST),
            (OpinionType.DUPLICATE.value, None, status.HTTP_201_CREATED),
            (
                OpinionType.DUPLICATE.value,
                "duplicate_reference",
                status.HTTP_400_BAD_REQUEST,
            ),
            (OpinionType.SPAM.value, None, status.HTTP_201_CREATED),
        ),
    )
    def test_create_opinion(
        self,
        api_client,
        default_opinion_data,
        test_opinion_payload,
        opinion_type,
        missing_field,
        expected_status,
    ):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ):
            with mock.patch("dook.core.integrations.chatbot.client.ApiClient"):
                news = NewsFactory()
                user = UserFactory(role=UserRoleType.FACT_CHECKER)
                UserNewsFactory(news=news, user=user)
                api_client.force_authenticate(user=user)

                payload = {
                    k: v
                    for k, v in test_opinion_payload(opinion_type=opinion_type).items()
                    if k != missing_field
                }
                url = reverse(
                    "news:crew:fact-checker-news-create-opinion", kwargs={"pk": news.pk}
                )

                response = api_client.post(url, data=payload)

                assert response.status_code == expected_status
                response_data = response.json()
                if response.status_code == status.HTTP_400_BAD_REQUEST:
                    assert (
                        response.json()["detail"]
                        == MissingFieldsException(missing_fields=(missing_field,)).detail
                    )
                elif response.status_code == status.HTTP_201_CREATED:
                    fact_checker_opinion = FactCheckerOpinion.objects.filter(
                        news=news, judge=user
                    ).first()
                    assert fact_checker_opinion

                    if opinion_type == OpinionType.VERDICT.value:
                        assert response_data["comment"] == payload["comment"]
                        assert (
                            response_data["confirmation_sources"]
                            == payload["confirmation_sources"]
                        )
                        assert response_data["verdict"] == payload["verdict"]
                        assert response_data["title"] == payload["title"]
                        assert response_data["is_duplicate"] is False
                        assert response_data["duplicate_reference"] is None
                    elif opinion_type == OpinionType.DUPLICATE.value:
                        assert response_data["comment"] == ""
                        assert response_data["confirmation_sources"] == ""
                        assert response_data["verdict"] == ""
                        assert response_data["title"] == ""
                        assert response_data["is_duplicate"] is True
                        assert response_data["duplicate_reference"] == str(
                            payload["duplicate_reference"]
                        )
                    elif opinion_type == OpinionType.SPAM.value:
                        assert response_data["comment"] == ""
                        assert response_data["confirmation_sources"] == ""
                        assert response_data["verdict"] == VerdictType.SPAM
                        assert response_data["title"] == ""
                        assert response_data["is_duplicate"] is False
                        assert response_data["duplicate_reference"] is None

    def test_notification(self, api_client, default_opinion_data):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ) as mocked:
            with mock.patch("dook.core.integrations.chatbot.client.ApiClient"):
                news = NewsFactory()
                user_1 = UserFactory(role=UserRoleType.FACT_CHECKER)
                user_2 = UserFactory(role=UserRoleType.FACT_CHECKER)

                UserNewsFactory(news=news, user=user_1)
                UserNewsFactory(news=news, user=user_2)

                url = reverse(
                    "news:crew:fact-checker-news-create-opinion", kwargs={"pk": news.pk}
                )

                api_client.force_authenticate(user=user_1)
                api_client.post(url, default_opinion_data, format="json")

                assert mocked["send_news_verified_notification"].called is False

                api_client.force_authenticate(user=user_2)
                response = api_client.post(url, default_opinion_data, format="json")

                assert response.status_code == 201

                email_args = {
                    "user_email": news.reporter_email,
                    "news_pk": news.pk,
                    "verdict_type": "VERIFIED_BY_FACT_CHECKER",
                }

                assert mocked["send_news_verified_notification"].called
                assert mocked["send_news_verified_notification"].call_args == mock.call(
                    **email_args
                )
