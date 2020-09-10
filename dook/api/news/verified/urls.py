from django.urls import path

from dook.api.news.verified.views import NewsVerifiedViewSet

urlpatterns = [
    path("news", NewsVerifiedViewSet.as_view(actions={"get": "list"}), name="news",),
    path(
        "news/<uuid:pk>",
        NewsVerifiedViewSet.as_view(actions={"get": "retrieve"}),
        name="news",
    ),
]
