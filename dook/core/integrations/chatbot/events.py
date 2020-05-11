from django.core.exceptions import ObjectDoesNotExist

from .client import ApiClient


class NewsNewVerdictSubscriber:
    @classmethod
    def receive(self, obj, *args, **kwargs):
        opinion = None
        try:
            opinion = obj.expertopinion
        except ObjectDoesNotExist:
            pass

        if not opinion:
            opinion = obj.factcheckeropinion_set.first()

        data = {
            "id": str(opinion.id),
            "title": opinion.title,
            "comment": opinion.comment,
            "confirmationSources": opinion.confirmation_sources,
            "verdict": obj._verdict,
            "news_id": str(obj.id),
            "text": obj.text,
        }
        ApiClient().send_new_news_verdict(data)
