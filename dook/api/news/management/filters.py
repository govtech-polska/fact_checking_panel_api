from django_filters.rest_framework import FilterSet, filters

from dook.api.news.verified.filters import NEWS_FINAL_VERDICT_TYPES
from dook.core.news.constants import NewsOrigin
from dook.core.news.models import News


class ManagementNewsFilter(FilterSet):
    current_verdict = filters.ChoiceFilter(
        field_name="current_verdict", choices=NEWS_FINAL_VERDICT_TYPES
    )
    deleted = filters.BooleanFilter(field_name="deleted")
    is_duplicate = filters.BooleanFilter(field_name="is_duplicate")
    is_pinned = filters.BooleanFilter(field_name="is_pinned")
    is_published = filters.BooleanFilter(field_name="is_published")
    is_sensitive = filters.BooleanFilter(field_name="is_sensitive")
    origin = filters.ChoiceFilter(field_name="origin", choices=NewsOrigin.choices)

    class Meta:
        model = News
        fields = (
            "current_verdict",
            "deleted",
            "is_duplicate",
            "is_pinned",
            "is_published",
            "is_sensitive",
            "origin",
        )
