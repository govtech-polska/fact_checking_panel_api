from pydoc import locate

from django.apps import AppConfig
from django.conf import settings

from dook.core.events.errors import EVENT_SUBSCRIBER_NOT_FOUND_ERROR


class EventsConfig(AppConfig):
    name = "dook.core.events"

    def ready(self):
        for subscribers in settings.EVENTS.values():
            for subscriber_path in subscribers:
                if not locate(subscriber_path):
                    raise ModuleNotFoundError(
                        EVENT_SUBSCRIBER_NOT_FOUND_ERROR.format(subscriber_path)
                    )
