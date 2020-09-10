from django_filters.rest_framework import FilterSet, filters

from dook.core.news.models import News


class NewsPublishedFilter(FilterSet):
    is_pinned = filters.BooleanFilter(field_name="is_pinned")

    class Meta:
        model = News
        fields = ("is_pinned",)
