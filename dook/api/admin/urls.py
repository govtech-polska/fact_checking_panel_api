from django.urls import path

from dook.api.admin.views import (
    ExpertListView,
    ExpertOpinionDetailView,
    FactCheckerListView,
    FactCheckerOpinionDetailView,
    InvitationListView,
    NewsDetailView,
    NewsImageView,
    NewsListView,
    SensitiveKeywordDetailView,
    SensitiveKeywordListView,
    UserDetailView,
)

urlpatterns = [
    path("experts", ExpertListView.as_view(), name="expert-list"),
    path("fact-checkers", FactCheckerListView.as_view(), name="fact-checker-list"),
    path("invitations", InvitationListView.as_view(), name="invitation-list"),
    path("users/<uuid:pk>", UserDetailView.as_view(), name="user-detail"),
    path("news/<uuid:pk>", NewsDetailView.as_view(), name="news-detail"),
    path("news", NewsListView.as_view(), name="news-list"),
    path(
        "keywords/<uuid:pk>", SensitiveKeywordDetailView.as_view(), name="keywords-detail"
    ),
    path("keywords", SensitiveKeywordListView.as_view(), name="keywords-list"),
    path(
        "expert-opinion/<int:pk>",
        ExpertOpinionDetailView.as_view(),
        name="expert-opinion-detail",
    ),
    path(
        "fact-checker-opinion/<int:pk>",
        FactCheckerOpinionDetailView.as_view(),
        name="fact-checker-opinion-detail",
    ),
    path("news-image/<uuid:pk>", NewsImageView.as_view(), name="news-image"),
]
