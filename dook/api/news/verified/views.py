from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from dook.api.news.verified.filters import NewsVerifiedFilter
from dook.api.news.verified.serializers import NewsVerifiedSerializer
from dook.core.news.models import Domain, News, Tag


class NewsVerifiedViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    lookup_url_kwarg = "pk"
    serializer_class = NewsVerifiedSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = NewsVerifiedFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["reported_at"]
    ordering = ["-reported_at"]
    search_fields = ["text"]

    def get_queryset(self):
        qs = (
            News.objects.with_fact_checker_opinions()
            .with_expert_opinions()
            .with_assigned_to_me(self.request.user)
            .with_verdicts()
            .filter(current_verdict__in=["true", "false", "unidentified"])
            .with_is_duplicate()
        )

        domains = self.request.query_params.getlist("domains[]")
        if domains:
            qs = qs.filter_by_related_domains(
                domains=[get_object_or_404(Domain, name=domain) for domain in domains]
            )

        tags = self.request.query_params.getlist("tags[]")
        if tags:
            qs = qs.filter_by_related_tags(
                tags=[get_object_or_404(Tag, name=name) for name in tags]
            )

        return qs
