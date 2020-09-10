from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status

from dook.api.news.consts import MAX_TAG_COUNT_PER_NEWS
from dook.core.news.constants import VerdictType

VALID_VERDICT_TYPES_FOR_OPINION_TYPE_VERDICT = (
    VerdictType.VERIFIED_TRUE.value,
    VerdictType.VERIFIED_FALSE.value,
    VerdictType.CANNOT_BE_VERIFIED.value,
)


class MissingFieldsException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "missing_fields"

    def __init__(self, missing_fields=[], *args, **kwargs):
        self.missing_fields = set(missing_fields)
        detail = _(f"Missing additional parameters: { {*missing_fields} }.")
        super().__init__(detail=detail, *args, **kwargs)


class SpamVerdictForVerdictOpinionTypeException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "spam_verdict_for_verdict_opinion_type"
    default_detail = _(
        f"Must provide one of { {*VALID_VERDICT_TYPES_FOR_OPINION_TYPE_VERDICT} }"
        f" for opinion type: `verdict`"
    )


class UserOpinionUniqueException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "user_opinion_unique_error"
    default_detail = _("Użytkownik może mieć tylko jedną opinię dla danego newsa.")


class DomainDoesNotExistException(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "domain_does_not_exist"
    default_detail = _("Domain does not exist.")


class TagCountPerNewsExceededException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "tag_count_per_news_exceeded"
    default_detail = _(
        f"Maximum number of tags: `{MAX_TAG_COUNT_PER_NEWS}` per news exceeded."
    )
