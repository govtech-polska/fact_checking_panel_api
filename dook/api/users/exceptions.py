from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status

from dook.api.users.consts import PROMOTABLE_ROLES


class DomainAssignToNonSpecialistRoleException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Can not assign domain to users who are not specialists.")
    default_code = "assign_domain_to_non_specialist"


class MissingDomainForSpecialistRoleException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Can not promote to specialist role without provided domain")
    default_code = "promote_to_specialist_without_provided_domain"


class UpdatingRoleNotDedicatedForPromotionException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Can not promote to roles other than {}.".format(PROMOTABLE_ROLES))
    default_code = "updating_role_not_dedicated_for_promotion"
