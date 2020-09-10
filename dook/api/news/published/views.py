from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny

from dook.api.news.published.filters import NewsPublishedFilter
from dook.api.news.published.serializers import NewsPublishedSerializer
from dook.core.news.models import Domain, News, Tag


class NewsPublishedViewSet(viewsets.ModelViewSet):
    serializer_class = NewsPublishedSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NewsPublishedFilter
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    permission_classes = (AllowAny,)

    def get_queryset(self):
        qs = News.objects.published()

        tags = self.request.query_params.getlist("tags[]")
        if tags:
            qs = qs.filter_by_related_tags(
                tags=[get_object_or_404(Tag, name=name) for name in tags]
            )

        domains = self.request.query_params.getlist("domains[]")
        if domains:
            qs = qs.filter_by_related_domains(
                domains=[get_object_or_404(Domain, name=domain) for domain in domains]
            )

        return qs
