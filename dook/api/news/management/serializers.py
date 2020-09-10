from rest_framework import serializers

from dook.api.news.keywords.serializers import (
    DomainSerializer,
    SensitiveKeywordSerializer,
    TagSerializer,
)
from dook.api.serializers import OpinionSerializerBase
from dook.core.news.models import ExpertOpinion, FactCheckerOpinion, News
from dook.core.users.constants import UserRoleType
from dook.core.users.models import Invitation, User


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role", "is_active"]


class BaseUserListSerializer(serializers.ModelSerializer):
    assigned = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "specialization",
            "created_at",
            "is_active",
            "assigned",
            "verified",
        ]

    def get_assigned(self, obj):
        return obj.assigned

    def get_verified(self, obj):
        return obj.verified


class ExpertListSerializer(BaseUserListSerializer):
    pass


class SpecialistListSerializer(BaseUserListSerializer):
    domain = DomainSerializer()

    class Meta:
        model = User
        fields = BaseUserListSerializer.Meta.fields + ["domain"]


class FactCheckerListSerializer(BaseUserListSerializer):
    pass


class InvitationListSerializer(serializers.ModelSerializer):
    expired = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = ["id", "email", "sent_at", "status", "expired"]

    def get_expired(self, obj):
        return obj.is_invalidated()


class JudgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name"]


class ExpertOpinionExtendedSerializer(OpinionSerializerBase):
    judge = JudgeSerializer(many=False, read_only=True)

    class Meta:
        model = ExpertOpinion
        fields = OpinionSerializerBase.Meta.fields + ("judge",)

    def update(self, instance, validated_data, *args, **kwargs):
        instance.reset_field_values(exclude_fields=set(validated_data.keys()))

        return super().update(instance, validated_data, *args, **kwargs)


class FactCheckerOpinionExtendedSerializer(OpinionSerializerBase):
    judge = JudgeSerializer(many=False, read_only=True)

    class Meta:
        model = FactCheckerOpinion
        fields = OpinionSerializerBase.Meta.fields + ("judge",)

    def update(self, instance, validated_data, *args, **kwargs):
        instance.reset_field_values(exclude_fields=set(validated_data.keys()))

        return super().update(instance, validated_data, *args, **kwargs)


class NewsSerializer(serializers.ModelSerializer):
    assigned_crew_member = serializers.SerializerMethodField()
    current_verdict = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()

    expert_opinion = ExpertOpinionExtendedSerializer(
        many=False, read_only=True, source="expertopinion"
    )
    fact_checker_opinions = FactCheckerOpinionExtendedSerializer(
        many=True, read_only=True, source="factcheckeropinion_set"
    )
    sensitive_keywords = SensitiveKeywordSerializer(many=True, read_only=True)

    domains = DomainSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = News
        read_only = True
        fields = (
            "assigned_crew_member",
            "comment",
            "current_verdict",
            "deleted",
            "domains",
            "expert_opinion",
            "fact_checker_opinions",
            "id",
            "is_duplicate",
            "is_pinned",
            "is_published",
            "is_sensitive",
            "origin",
            "reported_at",
            "screenshot_url",
            "sensitive_keywords",
            "tags",
            "text",
            "url",
        )

    def get_current_verdict(self, obj):
        return obj.current_verdict

    def get_is_duplicate(self, obj):
        return obj.is_duplicate

    def get_assigned_crew_member(self, obj):
        return obj.assigned_crew_member


class NewsUpdateSerializer(serializers.ModelSerializer):
    deleted = serializers.BooleanField(required=True)
    text = serializers.CharField(allow_null=False)
    comment = serializers.CharField(allow_null=False)
    url = serializers.CharField(required=False)
    domains = DomainSerializer(many=True, read_only=True)
    is_pinned = serializers.BooleanField(required=False)
    tags = TagSerializer(many=True, read_only=True)
    is_published = serializers.BooleanField(required=False)

    class Meta:
        model = News
        fields = (
            "deleted",
            "url",
            "text",
            "comment",
            "domains",
            "is_pinned",
            "tags",
            "is_published",
        )


class NewsImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)


class NewsAssignSerializer(serializers.Serializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            role__in=(UserRoleType.SPECIALIST, UserRoleType.EXPERT)
        )
    )
    replace_assignee = serializers.BooleanField(required=False)
