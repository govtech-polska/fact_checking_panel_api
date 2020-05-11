from unittest import mock

import pytest
from assertpy import assert_that
from django.urls import reverse
from rest_framework import status

from dook.core.news.constants import VerdictType
from dook.core.news.models import ExpertOpinion, FactCheckerOpinion
from dook.core.users.constants import UserRoleType
from tests.factories.news import (
    ExpertOpinionFactory,
    FactCheckerOpinionFactory,
    NewsFactory,
)
from tests.factories.users import UserFactory, UserNewsFactory


@pytest.fixture
def default_opinion_data():
    data = {
        "title": "Some random title",
        "about_corona_virus": True,
        "confirmation_sources": "drop.com",
        "verdict": VerdictType.VERIFIED_TRUE,
        "comment": "Thinking through all the facts and other dependencies, yes.",
        "is_duplicate": False,
    }
    return data


class TestExpertNewsViewSet:
    @pytest.mark.django_db
    def test_list(self, api_client):
        NewsFactory.create_batch(2)
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        response = api_client.get(reverse("api:expert-news-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    @pytest.mark.django_db
    def test_detail(self, api_client):
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        response = api_client.get(
            reverse("api:expert-news-detail", kwargs={"id": news.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.pk)

    @pytest.mark.django_db
    def test_create_expert_opinion(self, api_client, default_opinion_data):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ) as mocked:
            news = NewsFactory()
            user = UserFactory(role=UserRoleType.EXPERT)
            api_client.force_authenticate(user=user)

            url = reverse("api:expert-news-create_opinion", kwargs={"id": news.pk})
            response = api_client.post(url, default_opinion_data, format="json")

            expert_opinion = ExpertOpinion.objects.filter(news=news, judge=user).first()

            assert response.status_code == 201
            assert expert_opinion

            email_args = {
                "user_email": news.reporter_email,
                "news_pk": news.pk,
                "verdict_type": "VERIFIED_BY_EXPERT",
            }

            assert mocked["send_news_verified_notification"].called
            assert mocked["send_news_verified_notification"].call_args == mock.call(
                **email_args
            )

    @pytest.mark.django_db
    def test_already_verified_by_fcs(self, api_client, default_opinion_data):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ) as mocked:
            news = NewsFactory()
            user = UserFactory(role=UserRoleType.EXPERT)

            FactCheckerOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)
            FactCheckerOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)

            api_client.force_authenticate(user=user)

            url = reverse("api:expert-news-create_opinion", kwargs={"id": news.pk})
            response = api_client.post(url, default_opinion_data, format="json")

            expert_opinion = ExpertOpinion.objects.filter(news=news, judge=user).first()

            assert response.status_code == 201
            assert expert_opinion

            email_args = {
                "user_email": news.reporter_email,
                "news_pk": news.pk,
                "verdict_type": "VERIFIED_BY_EXPERT",
            }

            assert mocked["send_news_verified_notification"].called
            assert mocked["send_news_verified_notification"].call_args == mock.call(
                **email_args
            )

    @pytest.mark.django_db
    def test_already_opined(self, api_client, default_opinion_data):
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.EXPERT)
        ExpertOpinionFactory(news=news, judge=user)

        api_client.force_authenticate(user=user)

        url = reverse("api:expert-news-create_opinion", kwargs={"id": news.pk})
        response = api_client.post(url, default_opinion_data, format="json")

        assert response.status_code == 400
        assert_that(response.data["detail"].code).is_equal_to("user_opinion_unique_error")


class TestFactCheckerNewsViewSet:
    @pytest.mark.django_db
    def test_list(self, api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        [UserNewsFactory(user=user, news=news) for news in NewsFactory.create_batch(2)]

        api_client.force_authenticate(user=user)

        response = api_client.get(reverse("api:fc-news-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    @pytest.mark.django_db
    def test_detail(self, api_client):
        news = NewsFactory()
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        UserNewsFactory(user=user, news=news)
        api_client.force_authenticate(user=user)

        response = api_client.get(reverse("api:fc-news-detail", kwargs={"id": news.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.pk)

    @pytest.mark.django_db
    def test_create_fc_opinion(self, api_client, default_opinion_data):
        with mock.patch.multiple(
            "dook.core.users.events", send_news_verified_notification=mock.DEFAULT
        ) as mocked:
            news = NewsFactory()
            user_1 = UserFactory(role=UserRoleType.FACT_CHECKER)
            user_2 = UserFactory(role=UserRoleType.FACT_CHECKER)

            UserNewsFactory(news=news, user=user_1)
            UserNewsFactory(news=news, user=user_2)

            url = reverse("api:fc-news-create_opinion", kwargs={"id": news.pk})

            api_client.force_authenticate(user=user_1)
            api_client.post(url, default_opinion_data, format="json")

            fc_opinion = FactCheckerOpinion.objects.filter(
                news=news, judge=user_1
            ).first()

            assert fc_opinion
            assert mocked["send_news_verified_notification"].called is False

            api_client.force_authenticate(user=user_2)
            response = api_client.post(url, default_opinion_data, format="json")

            fc_opinion = FactCheckerOpinion.objects.filter(
                news=news, judge=user_2
            ).first()

            assert fc_opinion
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


class TestNewsVerifiedViewSet:
    @pytest.mark.django_db
    def test_list(self, api_client):
        url = reverse("api:news-verified-list")

        user = UserFactory(role=UserRoleType.EXPERT)
        news = NewsFactory.create_batch(2)
        [UserNewsFactory(user=user, news=news) for news in news]
        [
            ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.VERIFIED_TRUE)
            for news in news
        ]

        api_client.force_authenticate(user=user)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # not listing news without verdicts
        news = NewsFactory()
        UserNewsFactory(user=user, news=news)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # not listing spam
        news = NewsFactory()
        UserNewsFactory(user=user, news=news)
        ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.SPAM)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        news = NewsFactory()

        # not listing news with only one fact checker opinion
        fact_checker_1 = UserFactory(role=UserRoleType.FACT_CHECKER)
        UserNewsFactory(user=fact_checker_1, news=news)
        FactCheckerOpinionFactory(
            judge=fact_checker_1, news=news, verdict=VerdictType.VERIFIED_TRUE
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # listing news with at least two identical fc opinions
        fact_checker_2 = UserFactory(role=UserRoleType.FACT_CHECKER)
        UserNewsFactory(user=fact_checker_2, news=news)
        FactCheckerOpinionFactory(
            judge=fact_checker_2, news=news, verdict=VerdictType.VERIFIED_TRUE
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
