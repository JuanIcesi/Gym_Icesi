from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # 👈 IMPORT NECESARIO

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='auth/login.html'), name='logout'),
    path('', include('fit.urls')),  # rutas principales
]
