from rest_framework import serializers

from dook.api.news.keywords.exceptions import DomainDoesNotExistException
from dook.core.news.models import Domain, SensitiveKeyword, Tag


class SensitiveKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensitiveKeyword
        fields = ("created_at", "id", "name")


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ("created_at", "id", "name")


class DomainRelationField(serializers.RelatedField):
    def to_representation(self, domain):
        return DomainSerializer(domain, context=self.context).data

    def to_internal_value(self, pk):
        try:
            qs = self.get_queryset()
            return qs.get(id=pk)

        except Domain.DoesNotExist:
            raise DomainDoesNotExistException

    def get_queryset(self):
        return Domain.objects.all()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "created_at")
