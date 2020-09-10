from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class InternalEmailErrorException(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _("An internal email error has occurred, sending e-mail failed.")
    default_code = "email_error"


class UserAlreadyExistException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("An user with provided email address, already exists.")
    default_code = "provided_email_error"


class InvalidInviteTokenException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Provided invitation url is invalid.")
    default_code = "invalid_token_error"


class TokenAlreadyUsedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Registration link has been already used.")
    default_code = "invalid_token_error"


class InternalSignUpErrorException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("An error occurred. Registration process failed.")
    default_code = "sign_up_error"


class TokenExpiredException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Activation link expired.")
    default_code = "token_expired"


class EmailAlreadyConfirmedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("This account has been already confirmed.")
    default_code = "already_confirmed"


class InvalidActivationUrlException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Provided account activation url is invalid.")
    default_code = "invalid_activation_url"


class InactiveAccountException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("This User account is inactive.")
    default_code = "inactive_account"


class PasswordConfirmationFailedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Those passwords didn't match.")
    default_code = "password_confirmation_failed"


class EmailNotVerifiedException(exceptions.APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _(
        "The user's email has not been confirmed. Confirm this email address."
    )
    default_code = "email_not_verified"


class InvalidCredentialsException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("You have entered an invalid email or password")
    default_code = "invalid_credentials"


class UserDoesNotExistException(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("User does not exist.")
    default_code = "user_does_not_exist"


class PasswordTooWeakException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("The password you typed does not meet the password requirements.")
    default_code = "password_too_weak"


class InvalidPasswordException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("You have entered an invalid password")
    default_code = "invalid_password"


class InvitationAlreadyExistException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("An invitation mail has already been sent to this e-mail address.")
    default_code = "invitation_already_exist"


class MissingDomainForSpecialistInvitationException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Missing domain for specialist role")
    default_code = "missing_domain_for_specialist"
