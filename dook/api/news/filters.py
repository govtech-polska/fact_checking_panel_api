from django_filters.rest_framework import FilterSet, filters

from dook.core.news.models import News

NEWS_CURRENT_VERDICT_CHOICES = (
    ("true", "Verified True"),
    ("false", "Verified False"),
    ("spam", "Verified Spam"),
    ("unidentified", "Cannot be verified"),
    ("no_verdict", "No verdict"),
    ("dispute", "Dispute"),
)

NEWS_FINAL_VERDICT_TYPES = (
    ("no_verdict", "No verdict"),
    ("true", "Verified True"),
    ("false", "Verified False"),
    ("spam", "Verified Spam"),
    ("unidentified", "Cannot be verified"),
    ("awaiting", "Waiting for an expert's verdict"),
)


class ExpertNewsFilter(FilterSet):
    current_verdict = filters.ChoiceFilter(choices=NEWS_CURRENT_VERDICT_CHOICES)
    is_duplicate = filters.BooleanFilter(field_name="is_duplicate")
    is_about_corona_virus = filters.BooleanFilter(field_name="is_about_corona_virus")
    is_spam = filters.BooleanFilter(field_name="is_spam")
    is_sensitive = filters.BooleanFilter(field_name="is_sensitive")

    class Meta:
        model = News
        fields = (
            "current_verdict",
            "is_duplicate",
            "is_about_corona_virus",
            "is_spam",
            "is_sensitive",
        )


class FactCheckerNewsFilter(FilterSet):
    is_opined = filters.BooleanFilter(field_name="is_opined")

    class Meta:
        model = News
        fields = ("is_opined",)


class NewsVerifiedFilter(FilterSet):
    current_verdict = filters.ChoiceFilter(choices=NEWS_CURRENT_VERDICT_CHOICES)
    is_duplicate = filters.BooleanFilter(field_name="is_duplicate")
    is_about_corona_virus = filters.BooleanFilter(field_name="is_about_corona_virus")
    is_assigned_to_me = filters.BooleanFilter(field_name="is_assigned_to_me")

    class Meta:
        model = News
        fields = (
            "current_verdict",
            "is_duplicate",
            "is_about_corona_virus",
            "is_assigned_to_me",
        )


class AdminNewsFilter(FilterSet):
    current_verdict = filters.ChoiceFilter(
        field_name="current_verdict", choices=NEWS_FINAL_VERDICT_TYPES
    )
    is_duplicate = filters.BooleanFilter(field_name="is_duplicate")
    deleted = filters.BooleanFilter(field_name="deleted")
    is_sensitive = filters.BooleanFilter(field_name="is_sensitive")

    class Meta:
        model = News
        fields = (
            "current_verdict",
            "is_duplicate",
            "deleted",
            "is_sensitive",
        )
