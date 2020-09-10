from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status

from dook.core.news.constants import VerdictType
from tests.factories.news import (
    DomainFactory,
    ExpertOpinionFactory,
    FactCheckerOpinionFactory,
    NewsDomainFactory,
    NewsFactory,
    NewsTagFactory,
    TagFactory,
)


@pytest.mark.django_db
class TestNewsPublishedViewSet:
    list_url = reverse("news:published:news")

    def test_list(self, api_client):
        for verdict in (
            VerdictType.VERIFIED_TRUE,
            VerdictType.VERIFIED_FALSE,
            VerdictType.CANNOT_BE_VERIFIED,
        ):
            news = NewsFactory(is_published=True)
            ExpertOpinionFactory(news=news, verdict=verdict)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 3

        news = NewsFactory()
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)

        response = api_client.get(self.list_url)

        assert len(response.json()["results"]) == 4

    def test_list_filter_by_tags(self, api_client):
        news_1, news_2, news_3 = NewsFactory.create_batch(3, is_published=True)
        tag_1 = TagFactory()
        tag_2 = TagFactory()
        [NewsTagFactory(tag=tag_1, news=news) for news in (news_1, news_2)]
        NewsTagFactory(tag=tag_2, news=news_3)
        [
            ExpertOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)
            for news in (news_1, news_2, news_3)
        ]

        response = api_client.get(self.list_url, data={"tags[]": [tag_1.name]})

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 2
        assert all(
            item["id"] in (str(news_1.id), str(news_2.id)) for item in response_data
        )

        response = api_client.get(self.list_url, data={"tags[]": [tag_2.name]})

        response_data = response.json()["results"]
        assert len(response.json()["results"]) == 1
        assert response_data[0]["id"] == str(news_3.id)

    def test_list_filter_by_domains(self, api_client):
        news_1, news_2, news_3 = NewsFactory.create_batch(3, is_published=True)
        domain_1 = DomainFactory()
        domain_2 = DomainFactory()
        [NewsDomainFactory(domain=domain_1, news=news) for news in (news_1, news_2)]
        NewsDomainFactory(domain=domain_2, news=news_3)
        [
            ExpertOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)
            for news in (news_1, news_2, news_3)
        ]

        response = api_client.get(self.list_url, data={"domains[]": [domain_1.name]})

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 2
        assert all(
            item["id"] in (str(news_1.id), str(news_2.id)) for item in response_data
        )

        response = api_client.get(self.list_url, data={"domains[]": [domain_2.name]})

        response_data = response.json()["results"]
        assert len(response.json()["results"]) == 1
        assert response_data[0]["id"] == str(news_3.id)

    def test_list_ignore_not_verified_news(self, api_client):
        NewsFactory(is_published=True)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 0

    def test_list_ignore_deleted(self, api_client):
        news = NewsFactory(is_published=True, deleted=True)
        ExpertOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 0

    def test_list_ignore_verified_by_expert_but_not_published(self, api_client):
        ExpertOpinionFactory(
            news=NewsFactory(is_published=False), verdict=VerdictType.VERIFIED_TRUE
        )

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 0

    def test_list_ignore_duplicates(self, api_client):
        ExpertOpinionFactory(
            news=NewsFactory(is_published=True),
            is_duplicate=True,
            duplicate_reference=uuid4(),
        )

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 0

        news = NewsFactory(is_published=True)
        ExpertOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)
        FactCheckerOpinionFactory(
            news=news, is_duplicate=True, duplicate_reference=uuid4()
        )

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

    def test_list_fc_duplicate_verdicts_omitted(self, api_client):
        news = NewsFactory()
        FactCheckerOpinionFactory(
            news=news, is_duplicate=True, duplicate_reference=uuid4()
        )
        FactCheckerOpinionFactory.create_batch(
            2, news=news, verdict=VerdictType.VERIFIED_TRUE
        )

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1

    def test_list_ignore_spam(self, api_client):
        ExpertOpinionFactory(
            news=NewsFactory(is_published=True), verdict=VerdictType.SPAM,
        )
        news = NewsFactory()
        FactCheckerOpinionFactory.create_batch(2, news=news, verdict=VerdictType.SPAM)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 0

    def test_list_ignore_fact_checker_disputes(self, api_client):
        news = NewsFactory()
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.VERIFIED_TRUE)
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.VERIFIED_FALSE)

        news = NewsFactory()
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.SPAM)
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.CANNOT_BE_VERIFIED)

        for verdict_type in (VerdictType.VERIFIED_FALSE, VerdictType.VERIFIED_TRUE):
            news = NewsFactory()
            FactCheckerOpinionFactory(news=news, verdict=VerdictType.SPAM)
            FactCheckerOpinionFactory.create_batch(2, news=news, verdict=verdict_type)

        for verdict_type in (VerdictType.VERIFIED_FALSE, VerdictType.VERIFIED_TRUE):
            news = NewsFactory()
            FactCheckerOpinionFactory(news=news, verdict=VerdictType.CANNOT_BE_VERIFIED)
            FactCheckerOpinionFactory.create_batch(2, news=news, verdict=verdict_type)

        response = api_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 0

    def test_list_show_fc_opinions_compatible_with_expert_opinion(self, api_client):
        news = NewsFactory(is_published=True)
        FactCheckerOpinionFactory.create_batch(
            3, news=news, verdict=VerdictType.VERIFIED_TRUE
        )
        FactCheckerOpinionFactory.create_batch(
            2, news=news, verdict=VerdictType.VERIFIED_FALSE
        )
        FactCheckerOpinionFactory(news=news, verdict=VerdictType.CANNOT_BE_VERIFIED)
        expert_opinion = ExpertOpinionFactory(
            news=news, verdict=VerdictType.VERIFIED_TRUE
        )

        for verdict, expected_fc_opinion_count in (
            (VerdictType.VERIFIED_TRUE, 3),
            (VerdictType.VERIFIED_FALSE, 2),
            (VerdictType.CANNOT_BE_VERIFIED, 1),
        ):
            expert_opinion.verdict = verdict
            expert_opinion.comment = "comment"
            expert_opinion.title = "title"
            expert_opinion.confirmation_sources = "confirmation sources"
            expert_opinion.save()

            response = api_client.get(self.list_url)

            assert (
                len(response.json()["results"][0]["fact_checker_opinions"])
                == expected_fc_opinion_count
            )

    def test_detail(self, api_client):
        news = NewsFactory(is_published=True)
        expert_opinion = ExpertOpinionFactory(
            news=news, verdict=VerdictType.VERIFIED_TRUE
        )
        FactCheckerOpinionFactory.create_batch(
            2, news=news, verdict=VerdictType.VERIFIED_TRUE
        )

        response = api_client.get(reverse("news:published:news", kwargs={"pk": news.pk}))

        assert response.status_code == status.HTTP_200_OK
        response_news = response.json()
        assert response_news["id"] == str(news.pk)
        assert response_news["expert_opinion"]["title"] == expert_opinion.title
        assert len(response_news["fact_checker_opinions"]) == 2

        response = api_client.get(
            reverse("news:published:news", kwargs={"pk": str(uuid4())})
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
