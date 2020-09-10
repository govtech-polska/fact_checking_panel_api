from django_filters.rest_framework import FilterSet, filters

from dook.core.users.constants import InvitationStatusType, UserSpecializationType
from dook.core.users.models import Invitation, User


class CrewUsersFilter(FilterSet):
    specialization = filters.ChoiceFilter(
        field_name="specialization", choices=UserSpecializationType.choices
    )
    created = filters.DateFromToRangeFilter(field_name="created_at")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = User
        fields = ("specialization", "created", "is_active")


class InvitationFilter(FilterSet):
    status = filters.ChoiceFilter(
        field_name="status", choices=InvitationStatusType.choices
    )

    class Meta:
        model = Invitation
        fields = ("status",)
