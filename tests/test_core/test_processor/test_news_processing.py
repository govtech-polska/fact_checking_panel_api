import pytest
from assertpy import assert_that

from dook.core.news.models import News
from dook.core.processor.processor import NewsDraftProcessor
from tests.factories.news import NewsFactory, SensitiveKeywordFactory
from tests.factories.processor import NewsDraftFactory
from tests.factories.users import UserFactory


class TestNewsProcessing:
    NEWS_TEXT = (
        "Inspired by the character Noel from Celestial Method"
        ", this method set aims method to bring the cute and endearing theme onto GMK"
        "keycaps through light pastel colours and adorable novelty motifs."
    )
    NEWS_COMMENT = (
        "The Practice65 is a keyboard kit that contains almost "
        "everything you need to build your own keyboard from scratch"
    )

    @pytest.fixture()
    def default_news(self):
        news = NewsFactory(text=self.NEWS_TEXT, comment=self.NEWS_COMMENT)
        return news

    @pytest.fixture()
    def default_draft_news(self):
        news_draft = NewsDraftFactory(text=self.NEWS_TEXT, comment=self.NEWS_COMMENT)
        return news_draft

    @pytest.mark.django_db
    def test_get_keywords_out_of_text(self, default_news):
        keyword_1 = SensitiveKeywordFactory(name="noel")
        keyword_2 = SensitiveKeywordFactory(name="build")

        drafts_processor = NewsDraftProcessor()

        result = drafts_processor.get_keywords_out_of_text(default_news)

        assert_that(result).is_equal_to([keyword_1, keyword_2])

    @pytest.mark.django_db
    def test_assign_keywords_to_news(self, default_news):
        SensitiveKeywordFactory(name="fake")

        keywords = ["method", "theme", "keyboard", "build"]
        for name in keywords:
            SensitiveKeywordFactory(name=name)

        drafts_processor = NewsDraftProcessor()

        keywords_names = drafts_processor.get_keywords_out_of_text(default_news)

        drafts_processor.assign_keywords_to_news(keywords_names, default_news)

        news_keywords_names = [
            obj[0] for obj in default_news.sensitive_keywords.values_list("name")
        ]

        assert_that(news_keywords_names).is_equal_to(keywords)

    @pytest.mark.django_db
    def test_materialize_news_with_sensitive_keywords(self, default_draft_news):
        UserFactory.create_batch(10)
        SensitiveKeywordFactory(name="method")
        SensitiveKeywordFactory(name="keycap")

        draft_1 = NewsDraftFactory(text=self.NEWS_TEXT, comment=self.NEWS_COMMENT)
        draft_2 = NewsDraftFactory(
            text="Simple text, with some keycap.",
            comment="Simple comment, without any sensitive keywords.",
        )

        drafts_processor = NewsDraftProcessor()

        drafts_processor.assign_fact_checkers_to_materialized_news(draft_1)
        drafts_processor.assign_fact_checkers_to_materialized_news(draft_2)

        materialized_news_1 = News.objects.filter(url=draft_1.url).first()
        materialized_news_2 = News.objects.filter(url=draft_2.url).first()

        assert_that(materialized_news_1.is_sensitive).is_true()
        assert_that(materialized_news_2.is_sensitive).is_true()
