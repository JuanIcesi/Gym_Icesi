# fit/auth_views.py
"""
Vistas personalizadas de autenticación
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django import forms
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    """
    Vista de login personalizada que muestra mensajes de error más claros
    """
    template_name = "auth/login.html"
    
    def get_form(self, form_class=None):
        """
        Personalizar el formulario para mostrar mensajes de error más claros
        """
        form = super().get_form(form_class)
        
        # Personalizar el mensaje de error por defecto
        form.error_messages = {
            'invalid_login': (
                "El usuario o la contraseña son incorrectos. "
                "Por favor, verifica tus credenciales e intenta nuevamente."
            ),
            'inactive': "Esta cuenta está inactiva.",
        }
        
        return form
    
    def form_invalid(self, form):
        """
        Cuando el formulario es inválido (credenciales incorrectas),
        mostrar un mensaje claro al usuario
        """
        # Agregar mensaje adicional para mayor claridad
        if form.non_field_errors():
            messages.error(
                self.request,
                "Las credenciales ingresadas son incorrectas. Por favor, verifica tu usuario y contraseña.",
                extra_tags="login_error"
            )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Vista de logout personalizada que permite GET además de POST
    """
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get(self, request, *args, **kwargs):
        """
        Permitir logout con GET para facilitar el uso desde enlaces
        """
        return self.post(request, *args, **kwargs)

