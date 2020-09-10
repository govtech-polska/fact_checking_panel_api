from django.urls import path

from dook.api.news.crew.views import (
    ExpertNewsAssignTagsView,
    ExpertNewsCreateOpinionView,
    ExpertNewsDismissAssignmentView,
    ExpertNewsViewSet,
    FactCheckerNewsCreateOpinionView,
    FactCheckerNewsViewSet,
)

urlpatterns = [
    path(
        "expert/news",
        ExpertNewsViewSet.as_view(actions={"get": "list"}),
        name="expert-news",
    ),
    path(
        "expert/news/<uuid:pk>",
        ExpertNewsViewSet.as_view(actions={"get": "retrieve"}),
        name="expert-news",
    ),
    path(
        "expert/news/<uuid:pk>/create-opinion",
        ExpertNewsCreateOpinionView.as_view(),
        name="expert-news-create-opinion",
    ),
    path(
        "expert/news/<uuid:pk>/assign-tags",
        ExpertNewsAssignTagsView.as_view(),
        name="expert-news-assign-tags",
    ),
    path(
        "expert/news/<uuid:pk>/dismiss-assignment",
        ExpertNewsDismissAssignmentView.as_view(),
        name="expert-news-dismiss-assignment",
    ),
    path(
        "fact-checker/news",
        FactCheckerNewsViewSet.as_view(actions={"get": "list"}),
        name="fact-checker-news",
    ),
    path(
        "fact-checker/news/<uuid:pk>",
        FactCheckerNewsViewSet.as_view(actions={"get": "retrieve"}),
        name="fact-checker-news",
    ),
    path(
        "fact-checker/news/<uuid:pk>/create-opinion",
        FactCheckerNewsCreateOpinionView.as_view(),
        name="fact-checker-news-create-opinion",
    ),
]
