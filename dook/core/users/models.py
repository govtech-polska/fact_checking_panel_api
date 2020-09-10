import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from dook.core.users.constants import (
    InvitationStatusType,
    InvitationUserRoleType,
    UserRoleType,
    UserSpecializationType,
)
from dook.core.users.email_service import send_registration_invitation_email
from dook.core.users.managers import FactCheckersManager, UserManager, UserNewsManager


class User(AbstractBaseUser, PermissionsMixin):
    """ User model with UserRoleType choices representing role in system. """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=50, blank=False, unique=True)
    name = models.CharField(max_length=50, blank=False)
    role = models.CharField(
        max_length=30, choices=UserRoleType.choices, default=UserRoleType.FACT_CHECKER,
    )
    specialization = models.CharField(
        max_length=30,
        choices=UserSpecializationType.choices,
        default=UserSpecializationType.OTHER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    allow_subscriptions = models.BooleanField(default=True)

    news = models.ManyToManyField("news.News", through="UserNews")
    domain = models.ForeignKey("news.Domain", null=True, on_delete=models.SET_NULL)

    objects = UserManager()
    fact_checkers = FactCheckersManager()

    REQUIRED_FIELDS = ["name"]

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @staticmethod
    def check_if_user_exist(email):
        return User.objects.filter(email=email).exists()


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sent_at = models.DateField(blank=True, null=True)
    token = models.CharField(verbose_name=_("token"), max_length=64, unique=True)
    email = models.EmailField(
        unique=True,
        verbose_name=_("e-mail address"),
        error_messages={"unique": "Invitation with given email already exists."},
    )
    status = models.CharField(
        max_length=30,
        choices=InvitationStatusType.choices,
        default=InvitationStatusType.WAITING,
    )
    user_role = models.CharField(
        max_length=30,
        choices=InvitationUserRoleType.choices,
        default=InvitationUserRoleType.FACT_CHECKER,
    )
    domain = models.ForeignKey("news.Domain", null=True, on_delete=models.SET_NULL)

    @classmethod
    def create(cls, email, user_role, domain):
        token = cls.next_token()
        return cls._default_manager.create(
            email=email, token=token, user_role=user_role, domain=domain
        )

    @classmethod
    def next_token(cls):
        return get_random_string(64).lower()

    def key_expired(self):
        return (
            self.sent_at + timedelta(days=settings.INVITATION_EXPIRY)
            <= datetime.utcnow().date()
        )

    def is_invalidated(self):
        if self.key_expired() or self.status in (
            InvitationStatusType.FAILED,
            InvitationStatusType.USED,
        ):
            return True
        else:
            return False

    def send_invitation(self, request):
        invite_url = f"https://{settings.PANEL_DOMAIN_NAME}/register/{self.token}"
        return send_registration_invitation_email(email=self.email, invite_url=invite_url)

    def __str__(self):
        return f"Invite: {self.email}"


class UserNews(models.Model):
    """
    UserNews is an intermediate model between User and News.
    It is representing assigning News for User to review.
    """

    objects = UserNewsManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usernews_set",)
    news = models.ForeignKey("news.News", on_delete=models.CASCADE)
    assigned_by_email = models.EmailField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        unique_together = ["news", "user"]
