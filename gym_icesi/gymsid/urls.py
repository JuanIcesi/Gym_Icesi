# gymsid/urls.py
from django.contrib import admin
from django.urls import path, include
from fit.auth_views import CustomLoginView, CustomLogoutView

urlpatterns = [
    # Admin de Django (cambiar a django-admin para no conflictuar con nuestras URLs)
    path("django-admin/", admin.site.urls),

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

    # App fit (debe ir después para que capture admin/ antes que Django admin)
    path("", include("fit.urls")),
]
