from dook.api.news.errors import EVENT_MISSING_VERDICT_ATTRIBUTE_ERROR
from dook.core.events.services import ModelEventService


class NewsEvents(ModelEventService):
    def new_verdict(self, *args, **kwargs):
        if not hasattr(self.obj, "_verdict"):
            raise AttributeError(EVENT_MISSING_VERDICT_ATTRIBUTE_ERROR)

        self._send("news_new_verdict", *args, **kwargs)

    def edit_verdict(self, *args, **kwargs):
        if not hasattr(self.obj, "_verdict"):
            raise AttributeError(EVENT_MISSING_VERDICT_ATTRIBUTE_ERROR)

        self._send("news_edit_verdict", *args, **kwargs)
