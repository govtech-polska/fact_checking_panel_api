from rest_framework import serializers

from dook.core.news.models import (
    ExpertOpinion,
    FactCheckerOpinion,
    News,
    NewsSensitiveKeyword,
    Tag,
)


class ChatbotExpertOpinionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertOpinion
        fields = (
            "title",
            "confirmation_sources",
            "verdict",
            "comment",
            "is_duplicate",
            "duplicate_reference",
        )


class ChatbotFactCheckerOpinionSerializer(ChatbotExpertOpinionSerializer):
    class Meta(ChatbotExpertOpinionSerializer.Meta):
        model = FactCheckerOpinion
        fields = ChatbotExpertOpinionSerializer.Meta.fields


class ChatbotSensitiveKeywordSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="sensitive_keyword.name")

    class Meta:
        model = NewsSensitiveKeyword
        fields = ("name",)


class ChatbotTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "created_at")


class ChatbotExpertNewsTagsUpdateSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = ("tags",)


class ChatbotNewsSerializer(serializers.ModelSerializer):
    expertopinion = ChatbotExpertOpinionSerializer(many=False, read_only=True,)
    factcheckeropinion_set = ChatbotFactCheckerOpinionSerializer(
        many=True, read_only=True
    )

    current_verdict = serializers.SerializerMethodField()
    tags = ChatbotTagSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = (
            "id",
            "url",
            "screenshot_url",
            "text",
            "reported_at",
            "comment",
            "expertopinion",
            "factcheckeropinion_set",
            "current_verdict",
            "tags",
        )

    def get_current_verdict(self, obj):
        return obj._verdict
