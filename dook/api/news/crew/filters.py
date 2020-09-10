from django_filters.rest_framework import FilterSet, filters

from dook.core.news.constants import NewsOrigin
from dook.core.news.models import News

NEWS_CURRENT_VERDICT_CHOICES = (
    ("true", "Verified True"),
    ("false", "Verified False"),
    ("spam", "Verified Spam"),
    ("unidentified", "Cannot be verified"),
    ("no_verdict", "No verdict"),
    ("dispute", "Dispute"),
)


class ExpertNewsFilter(FilterSet):
    assigned_to_me = filters.BooleanFilter(field_name="is_assigned_to_me")
    current_verdict = filters.ChoiceFilter(choices=NEWS_CURRENT_VERDICT_CHOICES)
    is_duplicate = filters.BooleanFilter(field_name="is_duplicate")
    is_sensitive = filters.BooleanFilter(field_name="is_sensitive")
    is_spam = filters.BooleanFilter(field_name="is_spam")
    origin = filters.ChoiceFilter(field_name="origin", choices=NewsOrigin.choices)

    class Meta:
        model = News
        fields = (
            "assigned_to_me",
            "current_verdict",
            "is_duplicate",
            "is_sensitive",
            "is_spam",
            "origin",
        )


class FactCheckerNewsFilter(FilterSet):
    is_opined = filters.BooleanFilter(field_name="is_opined")
    origin = filters.ChoiceFilter(field_name="origin", choices=NewsOrigin.choices)

    class Meta:
        model = News
        fields = ("is_opined", "origin")
