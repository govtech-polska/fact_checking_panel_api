from django.db.models import Count
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from dook.api.news.keywords.exceptions import (
    DomainAssignedToUserInvitationOnDeleteException,
    DomainAssignedToUserOnDeleteException,
)
from dook.api.news.keywords.serializers import (
    DomainSerializer,
    SensitiveKeywordSerializer,
    TagSerializer,
)
from dook.api.permissions import (
    IsAdmin,
    IsExpert,
    IsFactChecker,
    IsModerator,
    IsSpecialist,
)
from dook.core.news.models import Domain, SensitiveKeyword, Tag
from dook.core.users.constants import InvitationStatusType
from dook.core.users.models import Invitation, User


class KeywordFilterMixin:
    filter_backends = [OrderingFilter, SearchFilter]
    ordering = ["name"]
    search_fields = ["name"]


class SensitiveKeywordViewSet(KeywordFilterMixin, viewsets.ModelViewSet):
    queryset = SensitiveKeyword.objects.all()
    serializer_class = SensitiveKeywordSerializer

    permission_classes = (IsAdmin | IsModerator,)


class DomainViewSet(KeywordFilterMixin, viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = (AllowAny,)
        elif self.action == "retrieve":
            self.permission_classes = (
                IsAdmin | IsModerator | IsExpert | IsSpecialist | IsFactChecker,
            )
        else:
            self.permission_classes = (IsAdmin | IsModerator,)

        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        users = User.objects.filter(domain=obj)
        if users:
            raise DomainAssignedToUserOnDeleteException

        user_invitations = Invitation.objects.filter(
            domain=obj.pk, status=InvitationStatusType.WAITING
        )
        if user_invitations:
            raise DomainAssignedToUserInvitationOnDeleteException

        return super().destroy(request, *args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer

    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = (AllowAny,)
        elif self.action == "retrieve":
            self.permission_classes = (
                IsAdmin | IsModerator | IsExpert | IsSpecialist | IsFactChecker,
            )
        elif self.action == "create":
            self.permission_classes = (IsAdmin | IsModerator | IsExpert | IsSpecialist,)
        else:
            self.permission_classes = (IsAdmin | IsModerator,)

        return super().get_permissions()

    def get_queryset(self):
        popular = self.request.query_params.get("popular")
        if popular:
            return Tag.objects.annotate(tag_count=Count("news_tag")).order_by(
                "-tag_count"
            )

        return Tag.objects.all().order_by("name")
