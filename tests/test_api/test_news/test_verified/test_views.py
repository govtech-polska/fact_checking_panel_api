from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status

from dook.core.news.constants import NewsOrigin, VerdictType
from dook.core.users.constants import UserRoleType
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


@pytest.mark.django_db
class TestNewsVerifiedViewSet:
    list_url = reverse("news:verified:news")

    def test_list(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        news = NewsFactory.create_batch(2)
        [UserNewsFactory(user=user, news=news) for news in news]
        [
            ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.VERIFIED_TRUE)
            for news in news
        ]

        api_client.force_authenticate(user=user)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # not listing news without verdicts
        news = NewsFactory()
        UserNewsFactory(user=user, news=news)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # not listing spam
        news = NewsFactory()
        UserNewsFactory(user=user, news=news)
        ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.SPAM)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        news = NewsFactory()

        # not listing news with only one fact checker opinion
        fact_checker_1 = UserFactory(role=UserRoleType.FACT_CHECKER)
        UserNewsFactory(user=fact_checker_1, news=news)
        FactCheckerOpinionFactory(
            judge=fact_checker_1, news=news, verdict=VerdictType.VERIFIED_TRUE
        )

        response = api_client.get(self.list_url)

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

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_list_filter_by_tags(self, api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        api_client.force_authenticate(user=user)

        tag_1, tag_2 = TagFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)
        [
            UserNewsFactory(user=user, news=news)
            for news in (news_1, news_2, news_3, news_4)
        ]
        [
            ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.VERIFIED_TRUE)
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

    def test_list_filter_by_domains(self, api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER)
        api_client.force_authenticate(user=user)

        domain_1, domain_2 = DomainFactory.create_batch(2)
        news_1, news_2, news_3, news_4 = NewsFactory.create_batch(4)
        [
            UserNewsFactory(user=user, news=news)
            for news in (news_1, news_2, news_3, news_4)
        ]
        [
            ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.VERIFIED_TRUE)
            for news in (news_1, news_2, news_3, news_4)
        ]

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

    def test_list_filter_by_origin(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        api_client.force_authenticate(user=user)

        news_plugin = NewsFactory(origin=NewsOrigin.PLUGIN)
        news_chatbot = NewsFactory(origin=NewsOrigin.CHATBOT)
        news_mobile = NewsFactory(origin=NewsOrigin.MOBILE)

        for news in (news_plugin, news_chatbot, news_mobile):
            UserNewsFactory(user=user, news=news)
            ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.VERIFIED_TRUE)

            response = api_client.get(self.list_url, data={"origin": news.origin})

            response_data = response.json()
            assert len(response_data["results"]) == 1
            assert response_data["results"][0]["id"] == str(news.id)

    def test_detail(self, api_client):
        user = UserFactory(role=UserRoleType.EXPERT)
        news = NewsFactory()
        UserNewsFactory(user=user, news=news)
        ExpertOpinionFactory(judge=user, news=news, verdict=VerdictType.VERIFIED_TRUE)

        api_client.force_authenticate(user=user)

        response = api_client.get(reverse("news:verified:news", kwargs={"pk": news.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(news.id)
