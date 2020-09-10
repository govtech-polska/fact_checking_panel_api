from rest_framework import serializers

from dook.api.news.keywords.serializers import (
    DomainSerializer,
    SensitiveKeywordSerializer,
    TagSerializer,
)
from dook.api.serializers import NewsSerializerBase, OpinionSerializerBase
from dook.core.news.models import ExpertOpinion, FactCheckerOpinion, News


class ExpertOpinionSerializer(OpinionSerializerBase):
    class Meta:
        model = ExpertOpinion
        fields = OpinionSerializerBase.Meta.fields


class FactCheckerOpinionSerializer(ExpertOpinionSerializer):
    class Meta(ExpertOpinionSerializer.Meta):
        model = FactCheckerOpinion
        fields = ExpertOpinionSerializer.Meta.fields


class ExpertOpinionShortSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField("get_date")

    def get_date(self, obj):
        return obj.created_at

    class Meta:
        model = ExpertOpinion
        fields = (
            "title",
            "confirmation_sources",
            "comment",
            "date",
            "verdict",
        )


class FactCheckerOpinionShortSerializer(ExpertOpinionShortSerializer):
    class Meta(ExpertOpinionShortSerializer.Meta):
        model = FactCheckerOpinion
        fields = ExpertOpinionShortSerializer.Meta.fields


class ExpertNewsSerializer(NewsSerializerBase):
    expert_opinion = ExpertOpinionSerializer(
        many=False, read_only=True, source="expertopinion"
    )
    fact_checker_opinions = FactCheckerOpinionSerializer(
        many=True, read_only=True, source="factcheckeropinion_set"
    )
    sensitive_keywords = SensitiveKeywordSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    domains = DomainSerializer(many=True, read_only=True)

    current_verdict = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()
    is_spam = serializers.SerializerMethodField()
    assigned_crew_member = serializers.SerializerMethodField()

    class Meta(NewsSerializerBase):
        model = News
        read_only = True
        fields = NewsSerializerBase.Meta.fields + (
            "assigned_crew_member",
            "current_verdict",
            "domains",
            "expert_opinion",
            "fact_checker_opinions",
            "is_duplicate",
            "is_published",
            "is_sensitive",
            "is_spam",
            "sensitive_keywords",
            "tags",
        )

    def get_current_verdict(self, obj):
        return obj.current_verdict

    def get_is_duplicate(self, obj):
        return obj.is_duplicate

    def get_is_spam(self, obj):
        return obj.is_spam

    def get_assigned_crew_member(self, obj):
        return obj.assigned_crew_member


class FactCheckerNewsSerializer(NewsSerializerBase):
    assigned_at = serializers.SerializerMethodField()
    is_opined = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta(NewsSerializerBase.Meta):
        model = News
        read_only = True
        fields = NewsSerializerBase.Meta.fields + ("assigned_at", "is_opined", "tags")

    def get_assigned_at(self, obj):
        return obj.assigned_at

    def get_is_opined(self, obj):
        return True if obj.is_opined else False


class ExpertNewsTagsUpdateSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = ("tags",)
