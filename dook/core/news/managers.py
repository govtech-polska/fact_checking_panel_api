from collections import Counter

from django.conf import settings
from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    CharField,
    Count,
    DateTimeField,
    Exists,
    F,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)

from dook.core.users.constants import UserRoleType
from dook.core.users.managers import ACTIVE_ASSIGNMENTS_BOUNDARY_EXPR
from dook.core.users.models import UserNews


class NewsQuerySet(models.QuerySet):
    def with_is_spam(self):
        return self.annotate(
            spam_verdicts_fc=Count(
                "factcheckeropinion", filter=Q(factcheckeropinion__verdict="spam")
            ),
            spam_verdicts_expert=Count(
                "expertopinion", filter=Q(expertopinion__verdict="spam")
            ),
        ).annotate(
            is_spam=Case(
                When(
                    (Q(spam_verdicts_fc__gte=2) | Q(spam_verdicts_expert__gte=1)),
                    then=Value(True),
                ),
                output_field=BooleanField(),
                default=Value(False),
            )
        )

    def with_is_duplicate(self):
        return self.annotate(
            is_duplicate_by_factcheckers=Count(
                "factcheckeropinion", filter=Q(factcheckeropinion__is_duplicate=True),
            )
        ).annotate(
            is_duplicate=Case(
                When(
                    expertopinion__is_duplicate__isnull=False,
                    then=F("expertopinion__is_duplicate"),
                ),
                When(is_duplicate_by_factcheckers__gte=2, then=Value(True)),
                output_field=BooleanField(),
                default=Value(False),
            )
        )

    def with_verdicts(self):
        return (
            self.with_fact_checker_opinions()
            .with_expert_opinions()
            .annotate(
                true=Count(
                    "factcheckeropinion", filter=Q(factcheckeropinion__verdict="true")
                ),
                false=Count(
                    "factcheckeropinion", filter=Q(factcheckeropinion__verdict="false")
                ),
                unidentified=Count(
                    "factcheckeropinion",
                    filter=Q(factcheckeropinion__verdict="unidentified"),
                ),
                spam_verdicts=Count(
                    "factcheckeropinion", filter=Q(factcheckeropinion__verdict="spam")
                ),
            )
            .annotate(
                current_verdict=Case(
                    When(
                        expertopinion__verdict__isnull=False,
                        then=F("expertopinion__verdict"),
                    ),
                    When(
                        (Q(true__gte=1) & Q(false__gte=1))
                        | (Q(spam_verdicts=1) & (Q(false__gte=1) | Q(true__gte=1)))
                        | (
                            Q(unidentified__gte=1)
                            & (Q(false__gte=1) | Q(true__gte=1) | Q(spam_verdicts=1))
                        ),
                        then=Value("dispute"),
                    ),
                    When(true__gte=2, then=Value("true")),
                    When(false__gte=2, then=Value("false")),
                    When(unidentified__gte=2, then=Value("unidentified"),),
                    When(spam_verdicts__gte=2, then=Value("spam")),
                    output_field=CharField(),
                    default=Value("no_verdict"),
                )
            )
        )

    def with_news_verdict_status(self):
        return (
            self.with_fact_checker_opinions()
            .annotate(confirmed=Count("factcheckeropinion"))
            .annotate(
                current_verdict=Case(
                    When(
                        expertopinion__verdict__isnull=False,
                        then=F("expertopinion__verdict"),
                    ),
                    When(confirmed__gt=0, then=Value("awaiting")),
                    When(confirmed=0, then=Value("no_verdict")),
                )
            )
            .distinct()
        )

    def with_has_user_opinion(self, user):
        return self.with_usernews_table().annotate(
            is_opined=Count(
                "factcheckeropinion", filter=Q(factcheckeropinion__judge=user)
            )
        )

    def with_assigned_at(self, user):
        return self.annotate(
            assigned_at=Case(
                When(usernews__user=user, then=F("usernews__created_at")),
                output_field=DateTimeField(),
                default=Value(None),
            )
        )

    def with_assigned_crew_members(self):
        assignments = UserNews.objects.filter(
            news=OuterRef("pk"),
            user__role__in=(UserRoleType.EXPERT, UserRoleType.SPECIALIST),
        )

        return self.annotate(
            assigned_crew_member=Subquery(assignments.values("user__email")[:1])
        )

    def with_assigned_to_me(self, user):
        assignments = UserNews.objects.filter(news=OuterRef("pk"), user=user,)
        return self.annotate(is_assigned_to_me=Exists(assignments))

    def for_user(self, user):

        return (
            self.filter(usernews__user=user).prefetch_related("usernews_set")
            if user.role == UserRoleType.FACT_CHECKER
            else self
        )

    def verified_by_expert(self, verified: bool = True):
        return self.exclude(expertopinion__isnull=verified)

    def with_fact_checker_opinions(self):

        return self.prefetch_related("factcheckeropinion_set")

    def with_expert_opinions(self):

        return self.prefetch_related("expertopinion")

    def with_usernews_table(self):

        return self.prefetch_related("usernews_set")

    def with_active_assignments_for_fact_checkers_count(self):
        return self.annotate(
            active_assignments_count=models.Count(
                "usernews",
                filter=self._active_assignments_filter_for_fact_checkers(),
                distinct=True,
            )
        )

    def _active_assignments_filter_for_fact_checkers(self):
        return Q(
            usernews__created_at__gte=ACTIVE_ASSIGNMENTS_BOUNDARY_EXPR,
            usernews__user__role=UserRoleType.FACT_CHECKER,
        )

    def filter_with_active_assignments_for_fact_checkers_below_target(self):
        return self.with_active_assignments_for_fact_checkers_count().filter(
            active_assignments_count__lt=settings.TARGET_ASSIGNMENTS_PER_NEWS_COUNT
        )

    def filter_without_verdict(self):
        return (
            self.filter(expertopinion__isnull=True)
            .annotate(Count("factcheckeropinion"))
            .filter(factcheckeropinion__count__lt=2)
        )

    def filter_by_related_tags(self, tags) -> models.QuerySet:
        from dook.core.news.models import NewsTag

        news_with_tags = list(
            NewsTag.objects.filter(tag__in=tags).values_list("news", flat=True)
        )
        news_ids = [
            id_ for id_, cnt in Counter(news_with_tags).items() if cnt == len(tags)
        ]

        return self.filter(id__in=news_ids)

    def filter_by_related_domains(self, domains) -> models.QuerySet:
        from dook.core.news.models import NewsDomain

        news_with_domains = list(
            NewsDomain.objects.filter(domain__in=domains).values_list("news", flat=True)
        )
        news_ids = [
            id_ for id_, cnt in Counter(news_with_domains).items() if cnt == len(domains)
        ]

        return self.filter(id__in=news_ids)


class NewsManager(models.Manager.from_queryset(NewsQuerySet)):
    def stale(self):
        return (
            self.filter_with_active_assignments_for_fact_checkers_below_target().filter_without_verdict()
        )

    def published(self):
        return (
            self.prefetch_related("factcheckeropinion_set")
            .prefetch_related("expertopinion")
            .exclude(
                Q(
                    Q(deleted=True)
                    | Q(Q(is_published=False) & Q(expertopinion__isnull=False))
                    | Q(
                        Q(is_published=True)
                        & Q(expertopinion__isnull=False)
                        & Q(expertopinion__is_duplicate=True)
                    )
                )
            )
            .annotate(
                true=Count(
                    "factcheckeropinion", filter=Q(factcheckeropinion__verdict="true")
                ),
                false=Count(
                    "factcheckeropinion", filter=Q(factcheckeropinion__verdict="false")
                ),
                unidentified=Count(
                    "factcheckeropinion",
                    filter=Q(factcheckeropinion__verdict="unidentified"),
                ),
                spam_verdicts=Count(
                    "factcheckeropinion", filter=Q(factcheckeropinion__verdict="spam")
                ),
            )
            .annotate(
                current_verdict=Case(
                    When(
                        expertopinion__verdict__isnull=False,
                        then=F("expertopinion__verdict"),
                    ),
                    When(
                        (Q(true__gte=1) & Q(false__gte=1))
                        | (Q(spam_verdicts=1) & (Q(false__gte=1) | Q(true__gte=1)))
                        | (
                            Q(unidentified__gte=1)
                            & (Q(false__gte=1) | Q(true__gte=1) | Q(spam_verdicts=1))
                        ),
                        then=Value("dispute"),
                    ),
                    When(true__gte=2, then=Value("true")),
                    When(false__gte=2, then=Value("false")),
                    When(unidentified__gte=2, then=Value("unidentified")),
                    When(spam_verdicts__gte=2, then=Value("spam")),
                    output_field=CharField(),
                    default=Value("no_verdict"),
                )
            )
            .exclude(current_verdict__in=["no_verdict", "spam", "dispute"])
        )


class NewsSensitiveKeywordsManager(models.Manager):
    def assign_keywords_to_news(self, sensitive_keywords, news):
        news_keywords = [
            self.model(sensitive_keyword=keyword, news=news)
            for keyword in sensitive_keywords
        ]
        self.bulk_create(news_keywords)
