import factory.fuzzy
from django.utils import timezone

from dook.api.news.consts import VERDICT_REQUIRED_FIELDS
from dook.core.news.constants import VerdictType
from dook.core.news.models import (
    Domain,
    ExpertOpinion,
    FactCheckerOpinion,
    News,
    NewsDomain,
    NewsSensitiveKeyword,
    NewsTag,
    OpinionBase,
    SensitiveKeyword,
    Tag,
)
from dook.core.users.constants import UserRoleType
from tests.factories.users import UserFactory


class NewsFactory(factory.DjangoModelFactory):
    class Meta:
        model = News

    url = factory.Faker("uri")
    screenshot_url = factory.Faker("uri")
    reporter_email = factory.Faker("email")
    reported_at = factory.LazyFunction(timezone.now)
    text = factory.Faker("text")
    comment = factory.Faker("sentence")


VERDICT_TYPES = [
    VerdictType.CANNOT_BE_VERIFIED,
    VerdictType.VERIFIED_FALSE,
    VerdictType.VERIFIED_TRUE,
    VerdictType.SPAM,
]


class OpinionBaseFactory(factory.DjangoModelFactory):
    class Meta:
        model = OpinionBase
        abstract = True

    news = factory.SubFactory(NewsFactory)
    title = factory.sequence(lambda x: f"title_{x}")
    comment = factory.Faker("text")
    verdict = factory.fuzzy.FuzzyChoice(choices=VERDICT_TYPES)
    confirmation_sources = factory.Faker("uri")

    @classmethod
    def _create(cls, *args, **kwargs):
        if kwargs.get("is_duplicate") is True:
            for field in VERDICT_REQUIRED_FIELDS:
                kwargs[field] = ""
        elif kwargs.get("verdict") == "spam":
            for field in VERDICT_REQUIRED_FIELDS:
                kwargs[field] = ""
            kwargs["verdict"] = VerdictType.SPAM

        return super()._create(*args, **kwargs)


class FactCheckerOpinionFactory(OpinionBaseFactory):
    class Meta:
        model = FactCheckerOpinion

    judge = factory.SubFactory(UserFactory, role=UserRoleType.FACT_CHECKER)


class ExpertOpinionFactory(OpinionBaseFactory):
    class Meta:
        model = ExpertOpinion

    judge = factory.SubFactory(UserFactory, role=UserRoleType.EXPERT)


class SensitiveKeywordFactory(factory.DjangoModelFactory):
    class Meta:
        model = SensitiveKeyword

    name = factory.sequence(lambda x: f"name_{x}")


class NewsSensitiveKeywordFactory(factory.DjangoModelFactory):
    class Meta:
        model = NewsSensitiveKeyword

    sensitive_keyword = factory.SubFactory("tests.factories.news.SensitiveKeywordFactory")
    news = factory.SubFactory("tests.factories.news.NewsFactory")


class DomainFactory(factory.DjangoModelFactory):
    class Meta:
        model = Domain

    name = factory.sequence(lambda x: f"name_{x}")


class NewsDomainFactory(factory.DjangoModelFactory):
    class Meta:
        model = NewsDomain

    news = factory.SubFactory("tests.factories.news.NewsFactory")
    domain = factory.SubFactory(DomainFactory)


class TagFactory(factory.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.sequence(lambda x: f"name_{x}")


class NewsTagFactory(factory.DjangoModelFactory):
    class Meta:
        model = NewsTag

    news = factory.SubFactory("tests.factories.news.NewsFactory")
    tag = factory.SubFactory(TagFactory)
