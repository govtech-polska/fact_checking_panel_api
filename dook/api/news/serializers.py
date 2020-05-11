from rest_framework import serializers

from dook.core.news.models import (
    ExpertOpinion,
    FactCheckerOpinion,
    News,
    NewsSensitiveKeyword,
)


class ExpertOpinionSerializer(serializers.ModelSerializer):
    """
    ExpertOpinionSerializer is actually base class for serializing and validating
    opinions both for expert opinion case and as inheritance for fact checker.
    """

    class Meta:
        model = ExpertOpinion
        fields = (
            "title",
            "about_corona_virus",
            "confirmation_sources",
            "verdict",
            "comment",
            "is_duplicate",
            "duplicate_reference",
        )


class FactCheckerOpinionSerializer(ExpertOpinionSerializer):
    class Meta(ExpertOpinionSerializer.Meta):
        model = FactCheckerOpinion
        fields = ExpertOpinionSerializer.Meta.fields


class SensitiveKeywordSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="sensitive_keyword.name")

    class Meta:
        model = NewsSensitiveKeyword
        fields = ("name",)


class NewsSerializerBase(serializers.ModelSerializer):
    """ Base Serializer Class for listing News instances """

    class Meta:
        fields = (
            "id",
            "url",
            "screenshot_url",
            "text",
            "reported_at",
            "comment",
        )


class ExpertNewsSerializer(NewsSerializerBase):
    expertopinion = ExpertOpinionSerializer(many=False, read_only=True)
    factcheckeropinion_set = FactCheckerOpinionSerializer(many=True, read_only=True)
    newssensitivekeyword_set = SensitiveKeywordSerializer(many=True, read_only=True,)

    current_verdict = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()
    is_about_corona_virus = serializers.SerializerMethodField()
    is_spam = serializers.SerializerMethodField()

    class Meta(NewsSerializerBase):
        model = News
        read_only = True
        fields = NewsSerializerBase.Meta.fields + (
            "current_verdict",
            "is_duplicate",
            "is_about_corona_virus",
            "expertopinion",
            "factcheckeropinion_set",
            "is_spam",
            "newssensitivekeyword_set",
            "is_sensitive",
        )

    def get_current_verdict(self, obj):
        return obj.current_verdict

    def get_is_duplicate(self, obj):
        return obj.is_duplicate

    def get_is_about_corona_virus(self, obj):
        return True if obj.is_about_corona_virus else False

    def get_is_spam(self, obj):
        return obj.is_spam


class FactCheckerNewsSerializer(NewsSerializerBase):
    assigned_at = serializers.SerializerMethodField()
    is_opined = serializers.SerializerMethodField()

    class Meta(NewsSerializerBase.Meta):
        model = News
        read_only = True
        fields = NewsSerializerBase.Meta.fields + ("assigned_at", "is_opined",)

    def get_assigned_at(self, obj):
        return obj.assigned_at

    def get_is_opined(self, obj):
        return True if obj.is_opined else False


class NewsVerifiedSerializer(NewsSerializerBase):
    expertopinion = ExpertOpinionSerializer(many=False, read_only=True,)
    factcheckeropinion_set = FactCheckerOpinionSerializer(many=True, read_only=True)

    current_verdict = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()
    is_about_corona_virus = serializers.SerializerMethodField()
    is_assigned_to_me = serializers.SerializerMethodField()

    class Meta(NewsSerializerBase.Meta):
        model = News
        fields = NewsSerializerBase.Meta.fields + (
            "expertopinion",
            "factcheckeropinion_set",
            "current_verdict",
            "is_duplicate",
            "is_about_corona_virus",
            "is_assigned_to_me",
        )

    def get_current_verdict(self, obj):
        return obj.current_verdict

    def get_is_duplicate(self, obj):
        return obj.is_duplicate

    def get_is_about_corona_virus(self, obj):
        return True if obj.is_about_corona_virus else False

    def get_is_assigned_to_me(self, obj):
        return obj.is_assigned_to_me
