from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class MissingFieldsException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "missing_fields"

    def __init__(self, missing_fields=[], *args, **kwargs):
        self.missing_fields = set(missing_fields)
        detail = _(f"Missing additional parameters: { {*missing_fields} }.")
        super().__init__(detail=detail, *args, **kwargs)


class RedundantFieldsException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "redundant_fields"

    def __init__(self, redundant_fields=[], *args, **kwargs):
        self.redundant_fields = set(redundant_fields)
        detail = _(f"Redundant fields: { {*self.redundant_fields} }.")
        super().__init__(detail=detail, *args, **kwargs)


class UserOpinionUniqueException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "user_opinion_unique_error"
    default_detail = _("Użytkownik może mieć tylko jedną opinię dla danego newsa.")
