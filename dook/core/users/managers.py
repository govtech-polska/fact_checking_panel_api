import datetime

from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q
from django.db.models.functions import Now

from dook.core.users.constants import UserRoleType, UserSpecializationType
from dook.core.users.errors import MISSING_EMAIL_ERROR, MISSING_USER_NAME_ERROR

ACTIVE_ASSIGNMENTS_BOUNDARY_EXPR = (
    Now()
    - datetime.timedelta(minutes=settings.ASSIGNMENT_ACTIVITY_PERIOD_MINUTES - 5)
    # 5 minutes margin to make sure we exclude all assignments from previous processor run
)


class UserQuerySet(models.QuerySet):
    def fact_checkers_with_opinions_count(self):
        return self.annotate(
            verified=models.Count("factcheckeropinion", distinct=True)
        ).filter(role=UserRoleType.FACT_CHECKER)

    def experts_with_opinions_count(self):
        return self.annotate(
            verified=models.Count("expertopinion", distinct=True)
        ).filter(role=UserRoleType.EXPERT)

    def with_assigned_news_count(self):
        return self.annotate(assigned=models.Count("usernews_set", distinct=True))

    def active_verified(self):
        return self.filter(is_active=True, is_verified=True)

    def with_active_assignments_count(self):
        return self.annotate(
            active_assignments_count=models.Count(
                "usernews_set", filter=self._active_assignments_filter(), distinct=True
            )
        )

    def _active_assignments_filter(self):
        return Q(usernews_set__created_at__gte=ACTIVE_ASSIGNMENTS_BOUNDARY_EXPR)

    def exclude_assigned_to_news(self, news):
        return self.exclude(usernews_set__news=news)

    def ordered_by_active_assignments(self):
        return self.with_active_assignments_count().order_by("active_assignments_count")


class UserManagerBase(BaseUserManager):
    def create_user(self, email, name, password, specialization=None, role=None):
        if not email:
            raise ValueError(MISSING_EMAIL_ERROR)
        if not name:
            raise ValueError(MISSING_USER_NAME_ERROR)

        email = email.lower()
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            role=role or UserRoleType.FACT_CHECKER,
            specialization=specialization or UserSpecializationType.OTHER,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email,
            password=password,
            name=name,
            role=UserRoleType.ADMIN,
            specialization=UserSpecializationType.OTHER,
        )

        user.is_active = True
        user.is_verified = True
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save()
        return user


class UserManager(UserManagerBase.from_queryset(UserQuerySet)):
    use_in_migrations = True


class FactCheckersManager(UserManager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(role=UserRoleType.FACT_CHECKER)


class UserNewsManager(models.Manager):
    def assign_users_to_news(self, users, news):
        user_news = [self.model(user=user, news=news) for user in users]
        self.bulk_create(user_news)
