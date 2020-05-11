from django.db import models


class NewsDraftQuerySet(models.QuerySet):
    def oldest_not_processed(self):
        return (
            self.using("readonly")
            .filter(processing_result__isnull=True)
            .order_by("reported_at")
        )


class NewsDraftManager(models.Manager.from_queryset(NewsDraftQuerySet)):
    pass
