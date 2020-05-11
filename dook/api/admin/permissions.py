from rest_framework.permissions import BasePermission

from dook.core.users.constants import UserRoleType


class IsFactChecker(BasePermission):
    """
    Allows access only to fact checkers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRoleType.FACT_CHECKER
        )


class IsExpert(BasePermission):
    """
    Allows access only to experts.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRoleType.EXPERT
        )


class IsAdmin(BasePermission):
    """
    Allow access only to admins.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRoleType.ADMIN
        )
