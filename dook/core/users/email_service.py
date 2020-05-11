from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string


def send_registration_confirm_email(url, user):
    REGISTRATION_CONFIRMATION_SUBJECT = "[DoFacts] Registration confirmation request."
    message = render_to_string(
        "account_activation_email.html", {"user_name": user.name, "url": url,},
    )

    email = EmailMessage(
        REGISTRATION_CONFIRMATION_SUBJECT,
        message,
        settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email.send()
    return check_email_status(email.anymail_status.status)


def send_account_confirmed_email(user):
    ACCOUNT_CONFIRMATION_SUBJECT = "[DoFacts] Account confirmed notification."
    message = render_to_string("account_confirmed_email.html", {"user_name": user.name,},)

    email = EmailMessage(
        ACCOUNT_CONFIRMATION_SUBJECT, message, settings.EMAIL_HOST_USER, to=[user.email]
    )
    email.send()
    return check_email_status(email.anymail_status.status)


def send_registration_invitation_email(email, invite_url):
    REGISTRATION_INVITATION_SUBJECT = (
        "[DoFacts] Invitation to register in the DoFacts App."
    )
    message = render_to_string(
        "registration_invitation_email.html", {"email": email, "invite_url": invite_url},
    )

    email = EmailMessage(
        REGISTRATION_INVITATION_SUBJECT, message, settings.EMAIL_HOST_USER, to=[email]
    )
    email.send()
    return check_email_status(email.anymail_status.status)


def send_registration_confirmation_email(name, email):
    REGISTRATION_CONFIRMATION_SUBJECT = "[DoFacts] Registration confirmation."
    message = render_to_string("registration_confirmation_email.html", {"name": name},)

    email = EmailMessage(
        REGISTRATION_CONFIRMATION_SUBJECT, message, settings.EMAIL_HOST_USER, to=[email]
    )
    email.send()
    return check_email_status(email.anymail_status.status)


def send_password_reset_email(email, reset_url):
    PASSWORD_RESET_SUBJECT = "[DoFacts] Password reset request."

    message = render_to_string("password_reset_email.html", {"reset_url": reset_url,},)

    email = EmailMessage(
        PASSWORD_RESET_SUBJECT, message, settings.EMAIL_HOST_USER, to=[email]
    )
    email.send()
    return check_email_status(email.anymail_status.status)


def check_email_status(status):
    if status:
        if status.issubset({"queued", "sent"}):
            return True
        else:
            return False
    else:
        return False


def assignment_notification_email_factory(user, news):
    SUBJECT = "[DoFacts] New verification request."
    url = get_news_url(news)
    message = render_to_string("assignment_notification_email.html", {"url": url},)

    return EmailMessage(
        subject=SUBJECT,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )


def get_news_url(news):
    return f"https://{settings.PANEL_DOMAIN_NAME}/submissions/{news.id}"


def send_multiple_assignment_notifications(users, news):
    messages = [assignment_notification_email_factory(user, news) for user in users]
    connection = get_connection()
    connection.send_messages(messages)


def send_news_verified_notification(user_email, news_pk, verdict_type):
    EMAIL_TEMPLATES = {
        "VERIFIED_BY_EXPERT": "news_verified_notification_by_expert.html",
        "VERIFIED_BY_FACT_CHECKER": "news_verified_notification_by_fc.html",
    }
    # swap url
    url = f"https://app.fakehunter.pap.pl/{news_pk}"

    NEWS_VERIFIED_SUBJECT = "[DoFacts] Your verification request has been checked."

    message = render_to_string(EMAIL_TEMPLATES[verdict_type], {"news_url": url,},)

    email = EmailMessage(
        NEWS_VERIFIED_SUBJECT, message, settings.EMAIL_HOST_USER, to=[user_email]
    )
    email.send()
    return check_email_status(email.anymail_status.status)
