from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class DomainDoesNotExistException(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "domain_does_not_exist"
    default_detail = _("Domain does not exist.")


class DomainAssignedToUserOnDeleteException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "domain_assigned_to_user"
    default_detail = _("Can not delete domain associated to auth.")


class DomainAssignedToUserInvitationOnDeleteException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "domain_assigned_to_user_invitation"
    default_detail = _(
        "Can not delete domain associated to auth with pending invitation."
    )
