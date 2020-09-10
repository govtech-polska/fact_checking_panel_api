from django.urls import path

from dook.api.news.keywords.views import (
    DomainViewSet,
    SensitiveKeywordViewSet,
    TagViewSet,
)

urlpatterns = [
    path(
        "sensitive",
        SensitiveKeywordViewSet.as_view(actions={"get": "list", "post": "create"}),
        name="sensitive-keywords",
    ),
    path(
        "sensitive/<uuid:pk>",
        SensitiveKeywordViewSet.as_view(
            actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="sensitive-keywords",
    ),
    path(
        "domains",
        DomainViewSet.as_view(actions={"get": "list", "post": "create"}),
        name="domains",
    ),
    path(
        "domains/<uuid:pk>",
        DomainViewSet.as_view(
            actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="domains",
    ),
    path(
        "tags",
        TagViewSet.as_view(actions={"get": "list", "post": "create"}),
        name="tags",
    ),
    path(
        "tags/<uuid:pk>",
        TagViewSet.as_view(
            actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="tags",
    ),
]
