import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from dook.core.news.models import News
from dook.core.processor.managers import NewsDraftManager


class ProcessingResult(models.TextChoices):
    ASSIGNED = "assigned", _("Assigned")
    DUPLICATE = "duplicate", _("Duplicate")


class NewsDraft(models.Model):

    objects = NewsDraftManager()

    class Meta:
        db_table = "news_draft"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,)
    url = models.URLField(max_length=2000)
    screenshot_url = models.CharField(max_length=1000, blank=True)
    reporter_email = models.EmailField(blank=False)
    reported_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    text = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    processing_result = models.CharField(
        max_length=30, choices=ProcessingResult.choices, default=None, null=True
    )

    def as_news(self) -> News:
        return News(
            url=self.url,
            screenshot_url=self.screenshot_url,
            reporter_email=self.reporter_email,
            reported_at=self.reported_at,
            text=self.text,
            comment=self.comment,
        )

    def mark_assigned(self):
        self.processing_result = ProcessingResult.ASSIGNED
        self.save(using="default")
