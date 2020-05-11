from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from dook.api.admin.permissions import IsExpert, IsFactChecker
from dook.api.news.filters import (
    ExpertNewsFilter,
    FactCheckerNewsFilter,
    NewsVerifiedFilter,
)
from dook.api.news.serializers import (
    ExpertNewsSerializer,
    ExpertOpinionSerializer,
    FactCheckerNewsSerializer,
    FactCheckerOpinionSerializer,
    NewsVerifiedSerializer,
)
from dook.core.news.models import News


class NewsViewSetBase(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    lookup_url_kwarg = "id"
    serializer_action_class = {}

    def get_serializer_class(self):
        return self.serializer_action_class.get(self.action, self.serializer_class)

    @action(methods=["post"], detail=True, url_name="create_opinion")
    def create_opinion(self, request, id):
        news_instance = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        opinion = news_instance.leave_opinion(
            user=self.request.user, opinion_params=serializer.validated_data
        )

        if news_instance.is_with_verdict():
            news_instance.events.new_verdict()

        serializer = self.get_serializer(instance=opinion)
        return Response(serializer.data, status=HTTP_201_CREATED)


class ExpertNewsViewSet(NewsViewSetBase):
    serializer_class = ExpertNewsSerializer
    serializer_action_class = {"create_opinion": ExpertOpinionSerializer}
    permission_classes = (IsExpert,)
    filterset_class = ExpertNewsFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["reported_at"]
    ordering = ["-reported_at"]
    search_fields = ["text"]

    def get_queryset(self):
        return (
            News.objects.with_fact_checker_opinions()
            .with_expert_opinions()
            .with_verdicts()
            .with_is_duplicate()
            .with_is_about_corona_virus()
            .with_is_spam()
        )


class FactCheckerNewsViewSet(NewsViewSetBase):
    serializer_class = FactCheckerNewsSerializer
    serializer_action_class = {"create_opinion": FactCheckerOpinionSerializer}
    permission_classes = (IsFactChecker,)
    filterset_class = FactCheckerNewsFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["assigned_at"]
    ordering = ["-assigned_at"]
    search_fields = ["text"]

    def get_queryset(self):
        return (
            News.objects.for_user(self.request.user)
            .with_has_user_opinion(self.request.user)
            .with_assigned_at(self.request.user)
            .with_verdicts()
            .filter(current_verdict__in=["no_verdict", "dispute"])
        )


class NewsVerifiedViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    lookup_url_kwarg = "id"
    serializer_class = NewsVerifiedSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = NewsVerifiedFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["reported_at"]
    ordering = ["-reported_at"]
    search_fields = ["text"]

    def get_queryset(self):
        return (
            News.objects.with_fact_checker_opinions()
            .with_expert_opinions()
            .with_assigned_to_me(self.request.user)
            .with_verdicts()
            .filter(current_verdict__in=["true", "false", "unidentified",])
            .with_is_duplicate()
            .with_is_about_corona_virus()
        )
