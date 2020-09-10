from rest_framework import serializers

from dook.api.news.crew.serializers import (
    ExpertOpinionShortSerializer,
    FactCheckerOpinionShortSerializer,
)
from dook.api.news.keywords.serializers import DomainSerializer, TagSerializer
from dook.core.news.models import News


class NewsPublishedSerializer(serializers.HyperlinkedModelSerializer):
    verdict = serializers.SerializerMethodField("get_verdict")
    verified_by_expert = serializers.SerializerMethodField("get_verified_by_expert")
    title = serializers.SerializerMethodField("get_title")
    text = serializers.SerializerMethodField("get_text")
    date = serializers.SerializerMethodField("get_date")

    expert_opinion = serializers.SerializerMethodField("get_expert_opinion")
    fact_checker_opinions = serializers.SerializerMethodField("get_fact_checker_opinions")

    tags = TagSerializer(many=True)
    domains = DomainSerializer(many=True)

    def get_verdict(self, obj):
        return obj.current_verdict

    def get_verified_by_expert(self, obj):
        return True if getattr(obj, "expertopinion", None) else False

    def get_title(self, obj):
        opinion = (
            getattr(obj, "expertopinion", None) or obj.factcheckeropinion_set.first()
        )

        return opinion.title if opinion else ""

    def get_text(self, obj):
        opinion = (
            getattr(obj, "expertopinion", None) or obj.factcheckeropinion_set.first()
        )

        return f"{opinion.comment[:200]}..." if opinion else ""

    def get_date(self, obj):
        return obj.created_at

    def get_expert_opinion(self, obj):
        expert_opinion = getattr(obj, "expertopinion", None)

        return (
            ExpertOpinionShortSerializer(expert_opinion).data if expert_opinion else None
        )

    def get_fact_checker_opinions(self, obj):
        fc_opinions = obj.factcheckeropinion_set.all()
        expert_opinion = self.get_expert_opinion(obj=obj)

        if expert_opinion:
            fc_opinions = [
                item for item in fc_opinions if item.verdict == expert_opinion["verdict"]
            ]

        return FactCheckerOpinionShortSerializer(fc_opinions, many=True).data

    class Meta:
        model = News
        read_only = True
        fields = (
            "date",
            "domains",
            "expert_opinion",
            "fact_checker_opinions",
            "id",
            "is_pinned",
            "reported_at",
            "screenshot_url",
            "tags",
            "text",
            "title",
            "url",
            "verdict",
            "verified_by_expert",
        )
