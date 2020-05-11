import logging

from anymail.exceptions import AnymailAPIError
from django.core.exceptions import ObjectDoesNotExist

from dook.api.users.exceptions import InternalEmailErrorException
from dook.core.users.email_service import send_news_verified_notification


class NewsNewVerdictSubscriber:
    @classmethod
    def receive(self, obj, *args, **kwargs):
        logger = logging.getLogger("events")

        try:
            obj.expertopinion
        except ObjectDoesNotExist:
            verdict_type = "VERIFIED_BY_FACT_CHECKER"
        else:
            verdict_type = "VERIFIED_BY_EXPERT"

        try:
            email_send = send_news_verified_notification(
                user_email=obj.reporter_email, news_pk=obj.id, verdict_type=verdict_type
            )
        except AnymailAPIError:
            logger.error(InternalEmailErrorException.default_detail)
        else:
            if email_send:
                logger.info(
                    f"Verification notification has been sent, for news with id: {obj.id}"
                )
            else:
                logger.error(
                    f"Verification notification sending failed, for news with id: {obj.id}"
                )
