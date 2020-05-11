from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from dook.api.users.exceptions import (
    EmailAlreadyConfirmedException,
    InvalidActivationUrlException,
    InvalidInviteTokenException,
)
from dook.core.users.models import User


def get_user_from_uid(uidb64):
    try:
        user_pk = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_pk)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise InvalidInviteTokenException
    else:
        return user


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.email)

    def validate_token(self, uidb64, token):
        user = get_user_from_uid(uidb64)
        if user is None or self.check_token(user, token) is False:
            raise InvalidActivationUrlException
        elif user.is_verified is True:
            raise EmailAlreadyConfirmedException
        else:
            pass


class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def validate_token(self, uidb64, token):
        user = get_user_from_uid(uidb64)
        if password_reset_token_generator.check_token(user, token) is False:
            raise InvalidInviteTokenException

    def make_url(self, user):
        token = password_reset_token_generator.make_token(user=user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"https://{settings.PANEL_DOMAIN_NAME}/reset-password/{uid}/{token}"
        return reset_url


account_activation_token_generator = AccountActivationTokenGenerator()
password_reset_token_generator = CustomPasswordResetTokenGenerator()
