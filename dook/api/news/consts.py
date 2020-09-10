from enum import Enum, unique
from typing import Set

MAX_TAG_COUNT_PER_NEWS = 6


@unique
class OpinionType(Enum):
    VERDICT = "verdict"
    SPAM = "spam"
    DUPLICATE = "duplicate"

    @classmethod
    def names(cls) -> Set[int]:
        return set(member.value for member in cls)


VERDICT_REQUIRED_FIELDS = {"title", "confirmation_sources", "comment", "verdict"}

DUPLICATE_REQUIRED_FIELDS = {
    "duplicate_reference",
}

OPINION_FIELDS = {
    "title",
    "confirmation_sources",
    "comment",
    "is_duplicate",
    "verdict",
    "duplicate_reference",
}
