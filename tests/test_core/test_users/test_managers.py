from datetime import timedelta
from random import randint

import pytest
from assertpy import assert_that
from django.test import override_settings
from django.utils import timezone

from dook.core.users.constants import UserRoleType
from dook.core.users.managers import UserQuerySet
from dook.core.users.models import User, UserNews
from tests.factories.news import ExpertOpinionFactory, FactCheckerOpinionFactory
from tests.factories.users import UserFactory, UserNewsFactory


@pytest.mark.django_db
class TestUserQuerySet:
    @pytest.fixture()
    def queryset(self):
        return UserQuerySet(model=User)

    def test_fact_checkers_with_opinions_count(self, queryset):
        _experts = UserFactory.create_batch(3, role=UserRoleType.EXPERT)
        fact_checkers = UserFactory.create_batch(3, role=UserRoleType.FACT_CHECKER)
        fact_checkers_opinions_counts = [
            len(FactCheckerOpinionFactory.create_batch(randint(1, 5), judge=checker))
            for checker in sorted(fact_checkers, key=lambda x: x.id)
        ]

        result = queryset.fact_checkers_with_opinions_count()

        assert_that(result).contains_only(*fact_checkers)
        assert_that(result).extracting("verified", sort="id").is_equal_to(
            fact_checkers_opinions_counts
        )

    def test_experts_with_opinions_count(self, queryset):
        _fact_checkers = UserFactory.create_batch(3, role=UserRoleType.FACT_CHECKER)
        experts = UserFactory.create_batch(3, role=UserRoleType.EXPERT)
        experts_opinions_counts = [
            len(ExpertOpinionFactory.create_batch(randint(1, 5), judge=expert))
            for expert in sorted(experts, key=lambda x: x.id)
        ]

        result = queryset.experts_with_opinions_count()

        assert_that(result).contains_only(*experts)
        assert_that(result).extracting("verified", sort="id").is_equal_to(
            experts_opinions_counts
        )

    def test_with_assigned_news_count(self, queryset):
        users = UserFactory.create_batch(3)
        assigned_news_counts = [
            len(UserNewsFactory.create_batch(randint(1, 5), user=user))
            for user in sorted(users, key=lambda x: x.id)
        ]

        result = queryset.with_assigned_news_count()

        assert_that(result).contains_only(*users)
        assert_that(result).extracting("assigned", sort="id").is_equal_to(
            assigned_news_counts
        )

    def test_active_verified(self, queryset):
        _active_user = UserFactory(is_active=True, is_verified=False)
        _verified_user = UserFactory(is_active=False, is_verified=True)
        active_verified_user = UserFactory(is_active=True, is_verified=True)

        result = queryset.active_verified()

        assert_that(result).contains_only(active_verified_user)

    def test_with_active_assignments_count(self, queryset):
        ACTIVITY_PERIOD = 100

        not_active_datetime = timezone.now() - timedelta(minutes=ACTIVITY_PERIOD + 1)

        users = UserFactory.create_batch(3)

        _not_active_assigned_news = [
            UserNewsFactory.create_batch(randint(1, 5), user=user,) for user in users
        ]
        UserNews.objects.update(created_at=not_active_datetime)

        active_assigned_news_counts = [
            len(UserNewsFactory.create_batch(randint(1, 5), user=user))
            for user in sorted(users, key=lambda x: x.id)
        ]

        with override_settings(ASSIGNMENT_ACTIVITY_PERIOD_MINUTES=ACTIVITY_PERIOD):
            result = queryset.with_active_assignments_count()

        assert_that(result).extracting("active_assignments_count", sort="id").is_equal_to(
            active_assigned_news_counts
        )


@pytest.mark.django_db
class TestFactCheckersManager:
    @pytest.fixture()
    def manager(self):
        return User.fact_checkers

    def test_queryset_returns_only_fact_checkers(self, manager):
        fact_checkers = UserFactory.create_batch(2, role=UserRoleType.FACT_CHECKER)
        _experts = UserFactory.create_batch(2, role=UserRoleType.EXPERT)
        _base_users = UserFactory.create_batch(2, role=UserRoleType.BASE_USER)

        result = manager.all()

        assert_that(result).contains_only(*fact_checkers)
