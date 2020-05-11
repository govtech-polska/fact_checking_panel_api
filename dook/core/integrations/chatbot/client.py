import requests

from django.conf import settings


class ApiClient:
    headers = {
        "x-api-key": settings.CHATBOT_API_KEY,
    }

    def _send(self, path, data):
        requests.post(
            f"{settings.CHATBOT_API_URL}{path}", json=data, headers=self.headers
        )

    def send_new_news_verdict(self, data):
        self._send("news", data)
