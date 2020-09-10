from django.urls import path

from dook.api.news.published.views import NewsPublishedViewSet

urlpatterns = [
    path("news", NewsPublishedViewSet.as_view(actions={"get": "list"}), name="news",),
    path(
        "news/<uuid:pk>",
        NewsPublishedViewSet.as_view(actions={"get": "retrieve"}),
        name="news",
    ),
]
