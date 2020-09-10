from django.urls import path

from dook.api.users.views import (
    CurrentUserView,
    EditSubscriptionView,
    ExpertListView,
    FactCheckerListView,
    InvitationListView,
    ModeratorListView,
    SpecialistListView,
    UserDetailView,
)

urlpatterns = [
    path("<uuid:pk>", UserDetailView.as_view(), name="user-detail"),
    path("current-user", CurrentUserView.as_view(), name="current-user"),
    path("moderators", ModeratorListView.as_view(), name="moderator-list"),
    path("experts", ExpertListView.as_view(), name="expert-list"),
    path("specialists", SpecialistListView.as_view(), name="specialist-list"),
    path("fact-checkers", FactCheckerListView.as_view(), name="fact-checker-list"),
    path("invitations", InvitationListView.as_view(), name="invitation-list"),
    path(
        "allow-subscriptions", EditSubscriptionView.as_view(), name="allow-subscriptions",
    ),
]
