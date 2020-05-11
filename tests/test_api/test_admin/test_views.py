import tempfile
from datetime import datetime
from unittest import mock
from uuid import uuid4

import pytest
from assertpy import assert_that
from django.urls import reverse
from PIL import Image
from rest_framework import status

from dook.core.news.constants import VerdictType
from dook.core.news.models import SensitiveKeyword
from dook.core.users.constants import UserRoleType
from dook.core.users.models import User
from tests.factories.news import (
    ExpertOpinionFactory,
    FactCheckerOpinionFactory,
    NewsFactory,
    SensitiveKeywordFactory,
)
from tests.factories.users import InvitationFactory, UserFactory


@pytest.fixture
def default_opinion_data():
    data = {
        "title": "Some random title",
        "about_corona_virus": True,
        "confirmation_sources": "drop.com",
        "verdict": VerdictType.VERIFIED_TRUE,
        "comment": "Thinking through all the facts and other dependencies, yes.",
        "is_duplicate": False,
        "duplicate_reference": None,
    }
    return data


class TestExpertListView:
    @pytest.mark.django_db
    def test_list(self, admin_api_client):
        UserFactory.create_batch(2, role=UserRoleType.EXPERT)
        UserFactory(role=UserRoleType.FACT_CHECKER)

        response = admin_api_client.get(reverse("admin:expert-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


class TestFactCheckerListView:
    @pytest.mark.django_db
    def test_list(self, admin_api_client):
        UserFactory.create_batch(2, role=UserRoleType.FACT_CHECKER)
        UserFactory(role=UserRoleType.EXPERT)

        response = admin_api_client.get(reverse("admin:fact-checker-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


class TestInvitationListView:
    @pytest.mark.django_db
    def test_list(self, admin_api_client):
        InvitationFactory.create_batch(2)

        response = admin_api_client.get(reverse("admin:invitation-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


class TestUserDetailView:
    @pytest.mark.django_db
    def test_detail(self, admin_api_client):
        user = UserFactory()

        response = admin_api_client.get(
            reverse("admin:user-detail", kwargs={"pk": user.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == user.role
        assert response.data["is_active"] == user.is_active

    def test_update(self, admin_api_client):
        user = UserFactory(role=UserRoleType.FACT_CHECKER, is_active=True)
        payload = {"role": UserRoleType.EXPERT, "is_active": False}

        response = admin_api_client.patch(
            reverse("admin:user-detail", kwargs={"pk": user.pk}), data=payload
        )

        user = User.objects.get(pk=user.pk)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == payload["role"]
        assert response.data["is_active"] == payload["is_active"]
        assert user.role == payload["role"]
        assert user.is_active == payload["is_active"]


class TestNewsListView:
    @pytest.mark.django_db
    def test_list(self, admin_api_client):
        NewsFactory.create_batch(2)

        response = admin_api_client.get(reverse("admin:news-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


class TestNewsDetailView:
    @pytest.mark.django_db
    def test_detail(self, admin_api_client):
        news = NewsFactory()

        response = admin_api_client.get(
            reverse(f"admin:news-detail", kwargs={"pk": news.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(news.id)

    @pytest.mark.django_db
    def test_update(self, admin_api_client):
        news = NewsFactory()
        new_text = "Wearing a foil hat, protects against coronavirus."
        data = {"text": new_text}

        url = reverse(f"admin:news-detail", kwargs={"pk": news.id})
        response = admin_api_client.patch(url, data, format="json")
        news.refresh_from_db()

        assert response.status_code == 200
        assert_that(news.text).is_equal_to(new_text)


class TestSensitiveKeywordListView:
    url = reverse("admin:keywords-list")

    @pytest.mark.django_db
    def test_list(self, admin_api_client):
        assert SensitiveKeyword.objects.count() == 0
        SensitiveKeywordFactory.create_batch(2)

        response = admin_api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    @pytest.mark.django_db
    def test_create(self, admin_api_client):
        assert SensitiveKeyword.objects.count() == 0

        payload = {"name": "test_name"}
        response = admin_api_client.post(self.url, data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == payload["name"]
        assert SensitiveKeyword.objects.count() == 1


class TestSensitiveKeywordDetailView:
    def test_detail(self, admin_api_client):
        keyword = SensitiveKeywordFactory()

        response = admin_api_client.get(
            reverse("admin:keywords-detail", kwargs={"pk": keyword.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(keyword.pk)

    def test_update(self, admin_api_client):
        keyword = SensitiveKeywordFactory()
        payload = {"name": f"{keyword.name}_1"}

        response = admin_api_client.patch(
            reverse("admin:keywords-detail", kwargs={"pk": keyword.pk}), data=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == payload["name"]
        assert SensitiveKeyword.objects.get(pk=keyword.pk).name == payload["name"]

    def test_delete(self, admin_api_client):
        keyword = SensitiveKeywordFactory()

        response = admin_api_client.delete(
            reverse("admin:keywords-detail", kwargs={"pk": keyword.pk})
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert SensitiveKeyword.objects.count() == 0


class TestExpertOpinionDetailView:
    @pytest.mark.django_db
    def test_update_opinion(self, admin_api_client, default_opinion_data):
        opinion = ExpertOpinionFactory(**default_opinion_data)

        update_opinion_data = default_opinion_data
        update_opinion_data["title"] = "Prohibition Ends At Last"

        url = reverse(f"admin:expert-opinion-detail", kwargs={"pk": opinion.id})
        response = admin_api_client.put(url, update_opinion_data, format="json",)

        opinion.refresh_from_db()

        assert response.status_code == 200
        assert_that(opinion.title).is_equal_to(update_opinion_data["title"])


class TestFactCheckerOpinionDetailView:
    @pytest.mark.parametrize(
        "is_duplicate, duplicate_reference, response_status",
        [(True, uuid4(), 200), (True, None, 400), (None, None, 400)],
    )
    @pytest.mark.django_db
    def test_update_duplicate_status(
        self,
        admin_api_client,
        is_duplicate,
        duplicate_reference,
        response_status,
        default_opinion_data,
    ):
        opinion = FactCheckerOpinionFactory(**default_opinion_data)
        update_opinion_data = {
            "is_duplicate": is_duplicate,
            "duplicate_reference": duplicate_reference,
        }

        url = reverse(f"admin:fact-checker-opinion-detail", kwargs={"pk": opinion.id})
        response = admin_api_client.put(url, update_opinion_data, format="json",)

        assert response.status_code == response_status

    def test_update_opinion(self, admin_api_client, default_opinion_data):
        opinion = FactCheckerOpinionFactory(**default_opinion_data)

        update_opinion_data = default_opinion_data
        update_opinion_data["title"] = "Prohibition Ends At Last"

        url = reverse(f"admin:fact-checker-opinion-detail", kwargs={"pk": opinion.id})
        response = admin_api_client.put(url, update_opinion_data, format="json",)

        opinion.refresh_from_db()

        assert response.status_code == 200

        assert_that(opinion.title).is_equal_to(update_opinion_data["title"])

    @pytest.mark.parametrize(
        "verdict, extra_data, response_status",
        [
            ("true", True, 200),
            ("spam", True, 400),
            ("spam", False, 200),
            ("true", False, 400),
            ("true", True, 200),
        ],
    )
    def test_update_verdict(
        self,
        admin_api_client,
        verdict,
        extra_data,
        response_status,
        default_opinion_data,
    ):
        opinion = FactCheckerOpinionFactory(**default_opinion_data)
        if extra_data is True:
            update_opinion_data = {
                "title": "some title",
                "comment": "some comment",
                "confirmation_sources": "drop.com",
                "about_corona_virus": True,
                "is_duplicate": False,
                "verdict": verdict,
                "duplicate_reference": None,
            }
        else:
            update_opinion_data = {"verdict": verdict}

        url = reverse(f"admin:fact-checker-opinion-detail", kwargs={"pk": opinion.id})
        response = admin_api_client.put(url, update_opinion_data, format="json",)

        assert response.status_code == response_status


class TestNewsImageView:
    @pytest.fixture
    def image_file(self):
        image = Image.new("RGB", (100, 100))

        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file)

        tmp_file.seek(0)
        return tmp_file

    @pytest.mark.django_db
    def test_upload_image(self, admin_api_client, image_file):
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
            url = reverse(f"admin:news-image", kwargs={"pk": news.id})

            response = admin_api_client.patch(
                url, {"image": image_file}, format="multipart"
            )
            news.refresh_from_db()

            assert response.status_code == 204
            assert_that(news.screenshot_url).is_equal_to(image_url)
