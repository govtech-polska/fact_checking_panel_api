from django.urls import include, path

urlpatterns = [
    path("crew/", include(("dook.api.news.crew.urls", "api"), namespace="crew")),
    path(
        "keywords/", include(("dook.api.news.keywords.urls", "api"), namespace="keywords")
    ),
    path(
        "management/",
        include(("dook.api.news.management.urls", "api"), namespace="management"),
    ),
    path(
        "published/",
        include(("dook.api.news.published.urls", "api"), namespace="published"),
    ),
    path(
        "verified/",
        include(("dook.api.news.verified.urls", "api"), namespace="verified"),
    ),
]
