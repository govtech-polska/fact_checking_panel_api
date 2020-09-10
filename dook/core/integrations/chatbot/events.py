from .client import ApiClient
from .serializers import ChatbotNewsSerializer


class ChatbotNewsBaseSubscriber:
    serializer = ChatbotNewsSerializer

    @classmethod
    def receive(cls, obj, *args, **kwargs):
        data = {"type": cls.event_type, "data": cls.serializer(obj).data}
        ApiClient().send_new_news_verdict(data)


class ChatbotNewsNewVerdictSubscriber(ChatbotNewsBaseSubscriber):
    event_type = "new_verdict"


class ChatbotNewsEditVerdictSubscriber(ChatbotNewsBaseSubscriber):
    event_type = "edit_verdict"
