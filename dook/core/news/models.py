import uuid
from collections import Counter

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models
from django.db.models import NOT_PROVIDED

from dook.api.news.consts import OPINION_FIELDS
from dook.api.news.exceptions import UserOpinionUniqueException
from dook.core.events.mixins import ModelEventMixin
from dook.core.integrations.storage.client import S3ApiClient
from dook.core.news.constants import NewsOrigin, VerdictType
from dook.core.news.events import NewsEvents
from dook.core.news.managers import NewsManager, NewsSensitiveKeywordsManager
from dook.core.users.constants import UserRoleType
from dook.core.users.models import User


class News(ModelEventMixin, models.Model):
    """
    News model representing object gathered from screenshot app.
    screenshot_url: identifies image resource on AWS S3.
    """

    url = models.URLField(max_length=2000)
    screenshot_url = models.CharField(max_length=1000, blank=True)
    reporter_email = models.EmailField(blank=False)
    text = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    origin = models.CharField(
        max_length=30, choices=NewsOrigin.choices, default=NewsOrigin.PLUGIN
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,)
    deleted = models.BooleanField(default=False)
    is_sensitive = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    reported_at = models.DateTimeField(auto_now=False, auto_now_add=False)

    sensitive_keywords = models.ManyToManyField(
        "news.SensitiveKeyword", through="NewsSensitiveKeyword"
    )
    domains = models.ManyToManyField(
        "news.Domain", through="NewsDomain", related_name="news"
    )
    tags = models.ManyToManyField("news.Tag", through="NewsTag", related_name="news")

    objects = NewsManager()
    events_class = NewsEvents

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_with_verdict():
            self.events.edit_verdict()

    def is_with_verdict(self):
        self._verdict = None
        expected_verditcs = [
            VerdictType.VERIFIED_TRUE.value,
            VerdictType.VERIFIED_FALSE.value,
            VerdictType.CANNOT_BE_VERIFIED.value,
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
            UserRoleType.SPECIALIST: ExpertOpinion,
            UserRoleType.MODERATOR: ExpertOpinion,
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
    is_duplicate = models.BooleanField(default=False)
    duplicate_reference = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        abstract = True
        unique_together = ["news", "judge"]

    def reset_field_values(self, exclude_fields):
        fields_to_reset = OPINION_FIELDS.difference(exclude_fields)
        for field in fields_to_reset:
            default_value = self._meta.get_field(field).default
            if default_value != NOT_PROVIDED:
                setattr(self, field, default_value)
            else:
                setattr(self, field, None)


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.news and self.news.is_with_verdict():
            self.news.events.edit_verdict()

    class Meta(OpinionBase.Meta):
        db_table = "fact_checker_opinion"


class ExpertOpinion(OpinionBase):
    """
    ExpertOpinion model is case specific for opinion judged by user
    with Expert role in the system.
    """

    news = models.OneToOneField(News, on_delete=models.CASCADE, primary_key=False,)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.news and self.news.is_with_verdict():
            self.news.events.edit_verdict()

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
    news = models.ForeignKey(
        News, on_delete=models.CASCADE, related_name="news_sensitive_keyword"
    )

    objects = NewsSensitiveKeywordsManager()


class Domain(Keyword):
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)


class NewsDomain(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="news_domain")
    domain = models.ForeignKey(
        Domain, on_delete=models.CASCADE, related_name="news_domain"
    )

    class Meta:
        unique_together = ["news", "domain"]


class Tag(Keyword):
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)


class NewsTag(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="news_tag")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="news_tag")

    class Meta:
        unique_together = ["news", "tag"]
