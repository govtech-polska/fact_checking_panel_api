from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("", lambda r: HttpResponse()),
    path("news/", include(("dook.api.news.urls", "news"), namespace="news")),
    path("auth/", include(("dook.api.auth.urls", "users"), namespace="auth")),
    path("users/", include(("dook.api.users.urls", "users"), namespace="users")),
]
