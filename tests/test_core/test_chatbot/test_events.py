from unittest import mock

import pytest
from django.urls import reverse

from dook.api.news.consts import OpinionType
from dook.core.integrations.chatbot.serializers import ChatbotNewsSerializer
from dook.core.news.constants import VerdictType
from dook.core.users.constants import UserRoleType
from tests.factories.news import (
    ExpertOpinionFactory,
    FactCheckerOpinionFactory,
    NewsFactory,
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
    }


class TestChatbotNewsSubscriber:
    @pytest.mark.django_db
    def test_new_expert_verdict(self, default_opinion_data, api_client):
        with mock.patch(
            "dook.core.integrations.chatbot.client.ApiClient._send"
        ) as mocked:
            with mock.patch("dook.core.users.events.NewsNewVerdictSubscriber"):
                default_opinion_data = {
                    **default_opinion_data,
                    **{"type": OpinionType.VERDICT.value},
                }

                news = NewsFactory()
                user = UserFactory(role=UserRoleType.EXPERT)
                api_client.force_authenticate(user=user)

                url = reverse(
                    "news:crew:expert-news-create-opinion", kwargs={"pk": news.pk}
                )
                api_client.post(url, default_opinion_data)

                news.refresh_from_db()
                news.is_with_verdict()

                assert mocked.called
                assert mocked.call_args == mock.call(
                    {"type": "new_verdict", "data": ChatbotNewsSerializer(news).data},
                    path="/news",
                )

    @pytest.mark.django_db
    def test_new_factcheckers_verdict(self, default_opinion_data, api_client):
        with mock.patch(
            "dook.core.integrations.chatbot.client.ApiClient._send"
        ) as mocked:
            with mock.patch("dook.core.users.events.NewsNewVerdictSubscriber"):
                default_opinion_data = {
                    **default_opinion_data,
                    **{"type": OpinionType.VERDICT.value},
                }

                news = NewsFactory()
                user_1 = UserFactory(role=UserRoleType.FACT_CHECKER)
                user_2 = UserFactory(role=UserRoleType.FACT_CHECKER)

                UserNewsFactory(news=news, user=user_1)
                UserNewsFactory(news=news, user=user_2)

                url = reverse(
                    "news:crew:fact-checker-news-create-opinion", kwargs={"pk": news.pk}
                )

                api_client.force_authenticate(user=user_1)
                api_client.post(url, default_opinion_data)

                assert mocked.called is False

                api_client.force_authenticate(user=user_2)
                api_client.post(url, default_opinion_data)

                news.refresh_from_db()
                news.is_with_verdict()

                assert mocked.called
                assert mocked.call_args == mock.call(
                    {"type": "new_verdict", "data": ChatbotNewsSerializer(news).data},
                    path="/news",
                )

    @pytest.mark.django_db
    def test_edit_expert_verdict(self, default_opinion_data, admin_api_client):
        with mock.patch(
            "dook.core.integrations.chatbot.client.ApiClient._send"
        ) as mocked:

            opinion = ExpertOpinionFactory(**default_opinion_data)

            update_opinion_data = default_opinion_data
            update_opinion_data["title"] = "Prohibition Ends At Last"
            update_opinion_data["type"] = OpinionType.VERDICT.value

            url = reverse(
                f"news:management:expert-opinion-detail", kwargs={"pk": opinion.id}
            )
            admin_api_client.put(url, update_opinion_data)

            opinion.refresh_from_db()
            opinion.news.is_with_verdict()

            assert mocked.called
            assert mocked.call_args == mock.call(
                {
                    "type": "edit_verdict",
                    "data": ChatbotNewsSerializer(opinion.news).data,
                },
                path="/news",
            )

    @pytest.mark.django_db
    def test_edit_factchecker_verdict(self, default_opinion_data, admin_api_client):
        with mock.patch(
            "dook.core.integrations.chatbot.client.ApiClient._send"
        ) as mocked:

            news = NewsFactory()
            FactCheckerOpinionFactory(**default_opinion_data, news=news)
            opinion = FactCheckerOpinionFactory(**default_opinion_data, news=news)

            update_opinion_data = default_opinion_data
            update_opinion_data["title"] = "Prohibition Ends At Last"
            update_opinion_data["type"] = OpinionType.VERDICT.value

            url = reverse(
                f"news:management:fact-checker-opinion-detail", kwargs={"pk": opinion.id}
            )
            admin_api_client.put(url, update_opinion_data)

            opinion.refresh_from_db()
            opinion.news.is_with_verdict()

            assert mocked.called
            assert mocked.call_args == mock.call(
                {
                    "type": "edit_verdict",
                    "data": ChatbotNewsSerializer(opinion.news).data,
                },
                path="/news",
            )

    @pytest.mark.django_db
    def test_edit_news_with_verdict(self, default_opinion_data, admin_api_client):
        with mock.patch(
            "dook.core.integrations.chatbot.client.ApiClient._send"
        ) as mocked:

            news = NewsFactory()
            FactCheckerOpinionFactory.create_batch(2, **default_opinion_data, news=news)

            data = {"text": "new text", "is_pinned": True}

            url = reverse(f"news:management:news", kwargs={"pk": news.id})
            admin_api_client.put(url, data)

            news.refresh_from_db()
            news.is_with_verdict()

            assert mocked.called
            assert mocked.call_args == mock.call(
                {"type": "edit_verdict", "data": ChatbotNewsSerializer(news).data},
                path="/news",
            )

    @pytest.mark.django_db
    def test_edit_news_without_verdict(self, default_opinion_data, admin_api_client):
        with mock.patch(
            "dook.core.integrations.chatbot.client.ApiClient._send"
        ) as mocked:

            news = NewsFactory()
            FactCheckerOpinionFactory(**default_opinion_data, news=news)

            data = {"text": "new text", "is_pinned": True}

            url = reverse(f"news:management:news", kwargs={"pk": news.id})
            admin_api_client.put(url, data)

            assert mocked.called is False
