from django_filters.rest_framework import FilterSet, filters

from dook.api.news.crew.filters import NEWS_CURRENT_VERDICT_CHOICES
from dook.core.news.constants import NewsOrigin
from dook.core.news.models import News

NEWS_FINAL_VERDICT_TYPES = (
    ("no_verdict", "No verdict"),
    ("true", "Verified True"),
    ("false", "Verified False"),
    ("spam", "Verified Spam"),
    ("unidentified", "Cannot be verified"),
    ("awaiting", "Waiting for an expert's verdict"),
)


class NewsVerifiedFilter(FilterSet):
    current_verdict = filters.ChoiceFilter(choices=NEWS_CURRENT_VERDICT_CHOICES)
    is_assigned_to_me = filters.BooleanFilter(field_name="is_assigned_to_me")
    is_duplicate = filters.BooleanFilter(field_name="is_duplicate")
    is_published = filters.BooleanFilter(field_name="is_published")
    origin = filters.ChoiceFilter(field_name="origin", choices=NewsOrigin.choices)

    class Meta:
        model = News
        fields = (
            "current_verdict",
            "is_assigned_to_me",
            "is_duplicate",
            "is_published",
            "origin",
        )
