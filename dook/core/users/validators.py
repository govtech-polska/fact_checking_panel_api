import re

from django.contrib.auth.password_validation import get_default_password_validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from dook.api.users.exceptions import PasswordTooWeakException


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Twoje hasło musi zawierać przynajmniej 1 wielką literę, A-Z.")


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall("[a-z]", password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _("Twoje hasło musi zawierać przynajmniej 1 małą literę, a-z.")


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall("[()[\]{}|\\`~!@#$%^&*_\-+=;:'\",<>./?]", password):
            raise ValidationError(
                _(
                    "Password must contain at lest one special character: "
                    + "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
                ),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return (
            _(
                "The password must contain at least 1 symbol: "
                + "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
            ),
        )


def validate_password(password, user=None, password_validators=None):
    errors = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise PasswordTooWeakException
