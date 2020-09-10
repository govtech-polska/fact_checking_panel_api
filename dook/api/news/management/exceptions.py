from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class DomainAssignedToUserOnDeleteException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "domain_assigned_to_user"
    default_detail = _("Can not delete domain associated to user.")


class DomainAssignedToUserInvitationOnDeleteException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "domain_assigned_to_user_invitation"
    default_detail = _(
        "Can not delete domain associated to auth with pending invitation."
    )


class NewsAlreadyAssignedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "news already assigned"
    default_detail = _("Can not assign news already assigned to another user.")


class NewsAlreadyAssignedToRequestedUserException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "news already assigned to requested user"
    default_detail = _("Can not assign news already assigned to requested user.")


class AssigningNewsToInactiveUserException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "assigning news to inactive user"
    default_detail = _("Can not assign news to inactive user.")
