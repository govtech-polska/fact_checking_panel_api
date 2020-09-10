from datetime import datetime, timedelta
from distutils.util import strtobool

from django.conf import settings
from django.db.models import BooleanField, Case, Q, Value, When
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, views
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dook.api.permissions import IsAdmin, IsModerator
from dook.api.users.consts import PROMOTABLE_ROLES
from dook.api.users.exceptions import (
    DomainAssignToNonSpecialistRoleException,
    MissingDomainForSpecialistRoleException,
    UpdatingRoleNotDedicatedForPromotionException,
)
from dook.api.users.filters import CrewUsersFilter, InvitationFilter
from dook.api.users.serializers import (
    CrewUserListSerializer,
    InvitationListSerializer,
    ModeratorSerializer,
    UserDetailSerializer,
    UserEditSubscriptionSerializer,
)
from dook.core.news.models import Domain
from dook.core.users.constants import InvitationStatusType, UserRoleType
from dook.core.users.models import Invitation, User, UserNews


class CrewListFilterMixin:
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name", "verified", "assigned", "created_at"]
    ordering = ["-name"]
    search_fields = ["name", "email"]
    filterset_class = CrewUsersFilter


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        data = {
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "allow_subscriptions": user.allow_subscriptions,
        }
        return Response(data)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer

    permission_classes = (IsAdmin,)

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])

    @staticmethod
    def update_role(user, new_role, domain=None):
        if user.role == new_role:
            return

        if user.role not in PROMOTABLE_ROLES or new_role not in PROMOTABLE_ROLES:
            raise UpdatingRoleNotDedicatedForPromotionException

        if new_role == UserRoleType.SPECIALIST and not domain:
            raise MissingDomainForSpecialistRoleException

        if (
            user.role in (UserRoleType.EXPERT, UserRoleType.SPECIALIST)
            and new_role == UserRoleType.MODERATOR
        ):
            UserNews.objects.filter(user=user).delete()

        if user.role == UserRoleType.SPECIALIST:
            user.domain = None

        user.role = new_role
        user.save()

    def partial_update(self, request, *args, **kwargs):
        domain = request.data.get("domain")
        role = request.data.get("role")
        user = self.get_object()

        if role:
            self.update_role(user=user, new_role=role, domain=domain)
        elif domain and user.role != UserRoleType.SPECIALIST:
            raise DomainAssignToNonSpecialistRoleException

        return super().partial_update(request, args, kwargs)


class ModeratorListView(CrewListFilterMixin, generics.ListAPIView):
    queryset = User.objects.moderators_with_opinion_count()
    serializer_class = ModeratorSerializer

    ordering_fields = ["name", "verified"]

    permission_classes = (IsAdmin,)


class ExpertListView(CrewListFilterMixin, generics.ListAPIView):
    queryset = User.objects.experts_with_opinions_count().with_assigned_news_count()
    serializer_class = CrewUserListSerializer

    permission_classes = (IsAdmin | IsModerator,)


class SpecialistListView(CrewListFilterMixin, generics.ListAPIView):
    serializer_class = CrewUserListSerializer

    permission_classes = (IsAdmin | IsModerator,)

    def get_queryset(self):
        qs = User.objects.specialists_with_opinions_count().with_assigned_news_count()

        domain_name = self.request.query_params.get("domain")
        if domain_name:
            domain = get_object_or_404(Domain, name=domain_name)
            qs = qs.filter(domain=domain)

        return qs


class FactCheckerListView(CrewListFilterMixin, generics.ListAPIView):
    queryset = User.objects.fact_checkers_with_opinions_count().with_assigned_news_count()
    serializer_class = CrewUserListSerializer

    permission_classes = (IsAdmin,)


class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationListSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = InvitationFilter
    ordering_fields = ["sent_at"]
    ordering = ["-sent_at"]

    permission_classes = (IsAdmin,)

    def get_queryset(self):
        qs = Invitation.objects.all()

        is_expired = self.request.query_params.get("is_expired")
        if is_expired:
            is_expired = bool(strtobool(is_expired))
            try:
                expiry_threshold = datetime.utcnow().date() - timedelta(
                    days=settings.INVITATION_EXPIRY
                )

                qs = qs.annotate(
                    is_expired=Case(
                        When(
                            (
                                Q(sent_at__lt=expiry_threshold)
                                & Q(status=InvitationStatusType.WAITING)
                            ),
                            then=Value(True),
                        ),
                        output_field=BooleanField(),
                        default=Value(False),
                    )
                ).filter(is_expired=is_expired)
            except ValueError:
                pass

        return qs


class EditSubscriptionView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        serializer = UserEditSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.allow_subscriptions = serializer.validated_data[
            "allow_subscriptions"
        ]
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
