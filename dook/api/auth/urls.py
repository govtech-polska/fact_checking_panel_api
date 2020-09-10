from django.urls import path

from dook.api.auth.views import (
    CreateInvitationView,
    CreateTokenView,
    InternalPasswordResetView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetView,
    SignUpView,
)

urlpatterns = [
    path("sign-up/<token>", SignUpView.as_view(), name="sign_up"),
    path("login", CreateTokenView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("send-invite", CreateInvitationView.as_view(), name="send_invite"),
    path(
        "reset-password-request",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "reset-password/<uidb64>/<token>",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "internal-reset-password",
        InternalPasswordResetView.as_view(),
        name="internal_password_reset",
    ),
]
