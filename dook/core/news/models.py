import uuid
from collections import Counter

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models
from django.db.models import NOT_PROVIDED

from dook.api.news.exceptions import (
    MissingFieldsException,
    RedundantFieldsException,
    UserOpinionUniqueException,
)
from dook.core.events.mixins import ModelEventMixin
from dook.core.integrations.storage.client import S3ApiClient
from dook.core.news.constants import (
    DUPLICATE_REQUIRED_FIELDS,
    OPINION_FIELDS,
    VERDICT_REQUIRED_FIELDS,
    VerdictType,
)
from dook.core.news.events import NewsEvents
from dook.core.news.managers import NewsManager, NewsSensitiveKeywordsManager
from dook.core.users.constants import UserRoleType
from dook.core.users.models import User


class News(ModelEventMixin, models.Model):
    """
    News model representing object gathered from screenshot app.
    screenshot_url: identifies image resource on AWS S3.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,)
    url = models.URLField(max_length=2000)
    screenshot_url = models.CharField(max_length=1000, blank=True)
    reporter_email = models.EmailField(blank=False)
    reported_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    text = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    deleted = models.BooleanField(default=False)

    sensitive_keywords = models.ManyToManyField(
        "news.SensitiveKeyword", through="NewsSensitiveKeyword"
    )

    objects = NewsManager()
    events_class = NewsEvents

    def is_with_verdict(self):
        self._verdict = None
        expected_verditcs = [
            VerdictType.VERIFIED_TRUE.value,
            VerdictType.VERIFIED_FALSE.value,
        ]

        try:
            self._verdict = (
                self.expertopinion.verdict
                if self.expertopinion.verdict in expected_verditcs
                else None
            )
        except ObjectDoesNotExist:
            pass

        if not self._verdict:
            counted_opinions_verdicts = Counter(
                self.factcheckeropinion_set.values_list("verdict", flat=True)
            )
            for v in expected_verditcs:
                if counted_opinions_verdicts[v] >= 2:
                    self._verdict = v

        return True if self._verdict else False

    def leave_opinion(self, user, opinion_params):
        whose_opinion = {
            UserRoleType.FACT_CHECKER: FactCheckerOpinion,
            UserRoleType.EXPERT: ExpertOpinion,
        }

        opinion_model = whose_opinion[user.role]

        try:
            opinion = opinion_model.objects.create(
                news=self, judge=user, **opinion_params
            )
        except (ValidationError, IntegrityError):
            raise UserOpinionUniqueException
        else:
            return opinion

    def attach_screenshot(self, image):
        s3_client = S3ApiClient()

        filename = s3_client.generate_filename(type="image")
        s3_client.upload_image(image_object=image, filename=filename)
        image_url = s3_client.get_object_url(object_name=filename)

        self.screenshot_url = image_url
        self.save()


class OpinionBase(models.Model):
    """
    OpinionBase model is a system base representation of opinion for
    corresponding News instance.
    """

    judge = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        related_query_name="%(class)s",
    )
    verdict = models.CharField(
        max_length=50, choices=VerdictType.choices, blank=True, default="",
    )

    title = models.TextField(blank=True, default="")
    comment = models.TextField(blank=True, default="")
    confirmation_sources = models.TextField(blank=True, default="")
    about_corona_virus = models.BooleanField(default=True)
    is_duplicate = models.BooleanField(default=False)
    duplicate_reference = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        abstract = True
        unique_together = ["news", "judge"]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.verdict == VerdictType.SPAM:
            self.check_fields_set({"verdict"})
            self.about_corona_virus = False
        elif self.is_duplicate is True:
            self.check_fields_set(DUPLICATE_REQUIRED_FIELDS)
        else:
            self.check_fields_set(VERDICT_REQUIRED_FIELDS)

    def reset_fields_values(self, exclude_fields):
        fields_to_reset = OPINION_FIELDS.difference(exclude_fields)
        for field in fields_to_reset:
            default_value = self._meta.get_field(field).default
            if default_value != NOT_PROVIDED:
                setattr(self, field, default_value)
            else:
                setattr(self, field, None)

    def check_fields_set(self, fields):
        missing_fields = []
        redundant_fields = []

        # Check for missing fields
        for field in fields:
            value = getattr(self, field)
            if value is None or value == "":
                missing_fields.append(field)

        # Check for redundant fields
        for field in OPINION_FIELDS.difference(fields):
            default_value = self._meta.get_field(field).default
            value = getattr(self, field)
            if value != default_value and value is not None:
                redundant_fields.append(field)

        if missing_fields:
            raise MissingFieldsException(missing_fields=missing_fields)

        if redundant_fields:
            raise RedundantFieldsException(redundant_fields=redundant_fields)


class FactCheckerOpinion(OpinionBase):
    """
    FastCheckerOpinion model is case specific for opinion judged by user
    with FastChecker role in the system.
    """

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        related_query_name="%(class)s",
    )

    class Meta(OpinionBase.Meta):
        db_table = "fact_checker_opinion"


class ExpertOpinion(OpinionBase):
    """
    ExpertOpinion model is case specific for opinion judged by user
    with Expert role in the system.
    """

    news = models.OneToOneField(News, on_delete=models.CASCADE, primary_key=False,)

    class Meta(OpinionBase.Meta):
        db_table = "expert_opinion"


class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,)
    name = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self._meta.model.__name__}, name: {self.name}"


class SensitiveKeyword(Keyword):
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)


class NewsSensitiveKeyword(models.Model):
    sensitive_keyword = models.ForeignKey(
        SensitiveKeyword,
        on_delete=models.CASCADE,
        related_name="newssensitivekeyword_set",
    )
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    objects = NewsSensitiveKeywordsManager()
