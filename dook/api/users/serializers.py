from rest_framework import serializers

from dook.api.news.keywords.serializers import DomainRelationField, DomainSerializer
from dook.core.users.models import Invitation, User


class CrewUserListSerializer(serializers.ModelSerializer):
    assigned = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    domain = DomainSerializer()

    class Meta:
        model = User
        fields = [
            "assigned",
            "created_at",
            "domain",
            "email",
            "id",
            "is_active",
            "name",
            "specialization",
            "verified",
        ]

    def get_assigned(self, obj):
        return obj.assigned

    def get_verified(self, obj):
        return obj.verified


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("created_at", "email", "id", "is_active", "name", "specialization")


class UserDetailSerializer(serializers.ModelSerializer):
    domain = DomainRelationField()

    class Meta:
        model = User
        fields = ("is_active", "domain", "email", "name", "role", "specialization")
        read_only_fields = ("email", "role")


class InvitationListSerializer(serializers.ModelSerializer):
    expired = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = ["id", "email", "sent_at", "status", "expired"]

    def get_expired(self, obj):
        return obj.is_invalidated()


class UserEditSubscriptionSerializer(serializers.Serializer):
    allow_subscriptions = serializers.BooleanField()
