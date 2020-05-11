from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("", lambda r: HttpResponse()),
    path("admin/", include(("dook.api.admin.urls", "admin"), namespace="admin")),
    path("api/", include(("dook.api.news.urls", "api"), namespace="api")),
    path("users/", include(("dook.api.users.urls", "users"), namespace="users")),
]
