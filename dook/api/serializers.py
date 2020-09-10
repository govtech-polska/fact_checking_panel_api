from rest_framework import serializers

from dook.api.news.consts import (
    DUPLICATE_REQUIRED_FIELDS,
    VERDICT_REQUIRED_FIELDS,
    OpinionType,
)
from dook.api.news.exceptions import (
    MissingFieldsException,
    SpamVerdictForVerdictOpinionTypeException,
)
from dook.core.news.constants import VerdictType


class NewsSerializerBase(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "comment",
            "origin",
            "reported_at",
            "screenshot_url",
            "text",
            "url",
        )


class OpinionSerializerBase(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=OpinionType.names(), write_only=True)

    class Meta:
        fields = (
            "comment",
            "confirmation_sources",
            "duplicate_reference",
            "id",
            "is_duplicate",
            "title",
            "type",
            "verdict",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        def _process_attrs_by_required_fields(_attrs, required_fields):
            missing_fields = {
                field
                for field in required_fields
                if field not in attrs or attrs[field] is None
            }

            if missing_fields:
                raise MissingFieldsException(missing_fields=missing_fields)

            for field in set(self.Meta.fields) - required_fields:
                attrs.pop(field, None)

            return _attrs

        opinion_type = attrs.pop("type")

        if opinion_type == OpinionType.VERDICT.value:
            attrs = _process_attrs_by_required_fields(
                _attrs=attrs, required_fields=VERDICT_REQUIRED_FIELDS
            )

            if attrs["verdict"] == VerdictType.SPAM.value:
                raise SpamVerdictForVerdictOpinionTypeException

            attrs["is_duplicate"] = False
        elif opinion_type == OpinionType.DUPLICATE.value:
            attrs = _process_attrs_by_required_fields(
                _attrs=attrs, required_fields=DUPLICATE_REQUIRED_FIELDS
            )
            attrs["is_duplicate"] = True
        elif opinion_type == OpinionType.SPAM.value:
            attrs = {"verdict": VerdictType.SPAM.value, "is_duplicate": False}

        return super().validate(attrs=attrs)
