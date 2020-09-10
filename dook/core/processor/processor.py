import logging
import math

from anymail.exceptions import AnymailError
from django.conf import settings
from django.db import transaction
from django.db.transaction import atomic

from dook.core.news.models import News, NewsSensitiveKeyword, SensitiveKeyword
from dook.core.processor.errors import (
    NEWS_DRAFT_PROCESSING_WITH_UNHANDLED_EXCEPTION_ERROR,
    NOTIFICATION_SENDING_FAILED_ERROR,
)
from dook.core.processor.models import NewsDraft
from dook.core.users import email_service
from dook.core.users.models import User, UserNews


class ProcessorBase:
    def __init__(self):
        self.logger = logging.getLogger("processor")

    def send_notifications_callback(self, checkers, news):
        def send_notifications():
            try:
                email_service.send_multiple_assignment_notifications(
                    [checker for checker in checkers if checker.allow_subscriptions],
                    news,
                )
            except AnymailError as e:
                self.logger.warning(NOTIFICATION_SENDING_FAILED_ERROR.format(e))

        return send_notifications


class NewsDraftProcessor(ProcessorBase):
    def __init__(self):
        super().__init__()
        self.fact_checkers = User.fact_checkers
        self.user_news = UserNews.objects
        self.drafts = NewsDraft.objects
        self.news_keywords = NewsSensitiveKeyword.objects
        self.keywords = self.get_keywords()

    def get_keywords(self):
        keywords = SensitiveKeyword.objects.all()
        return keywords

    def process_batch(self):
        news_drafts = self.next_batch()

        self.logger.info(f"Fetched batch of {len(news_drafts)} news drafts")

        for news_draft in news_drafts:
            try:
                self.process_draft(news_draft)
            except Exception:
                self.logger.exception(
                    NEWS_DRAFT_PROCESSING_WITH_UNHANDLED_EXCEPTION_ERROR.format(
                        news_draft
                    )
                )

    def next_batch(self):
        batch_size = self.get_batch_size()
        return self.drafts.oldest_not_processed()[:batch_size]

    def get_batch_size(self):
        # we want to assign one news per fact checker on average
        return int(
            math.ceil(
                self.fact_checkers.count() / settings.TARGET_ASSIGNMENTS_PER_NEWS_COUNT
            )
        )

    @atomic
    def process_draft(self, news_draft):
        self.logger.info(f"Processing {news_draft}")
        self.assign_fact_checkers_to_materialized_news(news_draft)

    def assign_fact_checkers_to_materialized_news(self, news_draft):
        checkers = self.get_checkers()
        news = self.materialize_news(news_draft)
        self.logger.info(f"Assigning {len(checkers)} fact checkers")
        self.user_news.assign_users_to_news(checkers, news)
        news_draft.mark_assigned()
        transaction.on_commit(lambda: self.send_notifications_callback(checkers, news))

    def get_checkers(self):
        return self.fact_checkers.active_verified().ordered_by_active_assignments_randomized()[
            : settings.TARGET_ASSIGNMENTS_PER_NEWS_COUNT
        ]

    def materialize_news(self, news_draft):
        news = news_draft.as_news()
        keywords = self.get_keywords_out_of_text(news)

        if len(keywords):
            self.assign_keywords_to_news(keywords, news)
            news.is_sensitive = True if keywords else False

        news.save()
        return news

    def get_keywords_out_of_text(self, news):
        associated_keywords = []
        text = news.text
        comment = news.comment
        for keyword in self.keywords:
            if keyword.name in text.lower() or keyword.name in comment.lower():
                associated_keywords.append(keyword)
        return associated_keywords

    def assign_keywords_to_news(self, keywords, news):
        self.news_keywords.assign_keywords_to_news(keywords, news)


class StaleNewsProcessor(ProcessorBase):
    def __init__(self,):
        super().__init__()
        self.fact_checkers = User.fact_checkers
        self.user_news = UserNews.objects
        self.news = News.objects

    def process_news(self):
        stale_news = self.get_stale_news_batch()

        self.logger.info(
            f"Assigning additional fact checkers to {len(stale_news)} stale news"
        )

        for news in stale_news:
            self.assign_additional_fact_checkers_to_stale_news(news)

    def get_stale_news_batch(self):
        stale_news = self.news.stale()
        limit = self.get_stale_news_batch_size()
        return stale_news[:limit]

    def get_stale_news_batch_size(self):
        # no more than one additional news for each fact checker
        return int(
            math.ceil(
                self.fact_checkers.count() / settings.TARGET_ASSIGNMENTS_PER_NEWS_COUNT
            )
        )

    @atomic
    def assign_additional_fact_checkers_to_stale_news(self, news):
        checkers = self.get_checkers(news)
        self.logger.info(f"Assigning {len(checkers)} fact checkers to {news}")
        self.user_news.assign_users_to_news(checkers, news)
        transaction.on_commit(lambda: self.send_notifications_callback(checkers, news))

    def get_checkers(self, news):
        missing = (
            settings.TARGET_ASSIGNMENTS_PER_NEWS_COUNT - news.factcheckeropinion__count
        )
        checkers = (
            self.fact_checkers.active_verified()
            .exclude_assigned_to_news(news)
            .ordered_by_active_assignments_randomized()[:missing]
        )
        return checkers
