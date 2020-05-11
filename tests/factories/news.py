import factory.fuzzy
from django.utils import timezone

from dook.core.news.constants import VERDICT_REQUIRED_FIELDS, VerdictType
from dook.core.news.models import (
    ExpertOpinion,
    FactCheckerOpinion,
    News,
    NewsSensitiveKeyword,
    OpinionBase,
    SensitiveKeyword,
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
    about_corona_virus = True

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

    keyword = factory.SubFactory("tests.factories.news.KeywordFactory")
    news = factory.SubFactory("tests.factories.news.NewsFactory")
