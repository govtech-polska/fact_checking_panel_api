from rest_framework import serializers

from dook.api.news.crew.serializers import (
    ExpertOpinionSerializer,
    FactCheckerOpinionSerializer,
)
from dook.api.serializers import NewsSerializerBase
from dook.core.news.models import News


class NewsVerifiedSerializer(NewsSerializerBase):
    expert_opinion = ExpertOpinionSerializer(
        many=False, read_only=True, source="expertopinion"
    )
    fact_checker_opinions = FactCheckerOpinionSerializer(
        many=True, read_only=True, source="factcheckeropinion_set"
    )

    current_verdict = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()
    is_assigned_to_me = serializers.SerializerMethodField()

    class Meta(NewsSerializerBase.Meta):
        model = News
        fields = NewsSerializerBase.Meta.fields + (
            "current_verdict",
            "expert_opinion",
            "fact_checker_opinions",
            "is_assigned_to_me",
            "is_duplicate",
            "is_published",
            "origin",
        )

    def get_current_verdict(self, obj):
        return obj.current_verdict

    def get_is_duplicate(self, obj):
        return obj.is_duplicate

    def get_is_assigned_to_me(self, obj):
        return obj.is_assigned_to_me
