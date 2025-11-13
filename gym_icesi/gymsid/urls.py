# gymsid/urls.py
from django.contrib import admin
from django.urls import path, include
from fit.auth_views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),

    # LOGIN / LOGOUT
    path(
        "login/",
        CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        CustomLogoutView.as_view(),
        name="logout",
    ),

    # App fit
    path("", include("fit.urls")),
]
