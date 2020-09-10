from pydoc import locate

from django.conf import settings


class ModelEventService:
    def __init__(self, instance):
        self.obj = instance

    def _send(self, event_name, *args, **kwargs):
        for subscriber_path in settings.EVENTS[event_name]:
            locate(subscriber_path).receive(self.obj, *args, **kwargs)
