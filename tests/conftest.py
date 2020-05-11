import pytest
from pytest_django.lazy_django import skip_if_no_django

from dook.core.users.models import User


@pytest.fixture()
def api_rf():
    skip_if_no_django()
    from rest_framework.test import APIRequestFactory

    return APIRequestFactory()


@pytest.fixture()
def api_client():
    skip_if_no_django()
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture()
def admin_api_client(db, admin_user):
    """A Django test client logged in as an admin user."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture()
def default_user(db, django_user_model):

    email = "user@example.com"

    user, created = User.objects.get_or_create(email=email)
    user.set_password("password")
    user.save()
    return user


@pytest.fixture()
def authenticated_api_client(db, default_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=default_user)
    return client
