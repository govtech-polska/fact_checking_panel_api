from dook.core.news.models import News


def trigger_new_verdict_event_for_news():
    for news in News.objects.with_verdicts():
        if news.is_with_verdict():
            news.events.new_verdict()
