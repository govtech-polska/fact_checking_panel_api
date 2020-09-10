from django.urls import path

from dook.api.news.management.views import (
    ExpertOpinionDetailView,
    FactCheckerOpinionDetailView,
    NewsAssignView,
    NewsDismissView,
    NewsImageView,
    NewsViewSet,
)

urlpatterns = [
    path("news", NewsViewSet.as_view(actions={"get": "list"}), name="news"),
    path(
        "news/<uuid:pk>",
        NewsViewSet.as_view(actions={"get": "retrieve", "patch": "partial_update"}),
        name="news",
    ),
    path("news/<uuid:pk>/assign", NewsAssignView.as_view(), name="news-assign"),
    path(
        "news/<uuid:pk>/dismiss-assignment",
        NewsDismissView.as_view(),
        name="news-dismiss-assignment",
    ),
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
