# fit/auth_backend.py
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from django.db import OperationalError, DatabaseError
from .institutional_models import InstitutionalUser

def _role_flags(role: str):
    role = (role or "").upper()
    if role == "ADMIN":
        return dict(is_staff=True, is_superuser=True)
    if role == "EMPLOYEE":
        return dict(is_staff=True, is_superuser=False)
    return dict(is_staff=False, is_superuser=False)  # STUDENT u otros

class InstitutionalBackend(BaseBackend):
    """
    Autentica contra la tabla institucional 'users'.
    Regla demo: password válido = password_hash sin 'hash_'.
    Ej: 'hash_jp123' -> contraseña 'jp123'.
    
    Maneja errores cuando la BD institucional no está disponible (SQLite local).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        try:
            # Intentar obtener el usuario de la BD institucional
            iu = InstitutionalUser.objects.get(username=username, is_active=True)
        except InstitutionalUser.DoesNotExist:
            # Usuario no existe en la BD institucional
            return None
        except (OperationalError, DatabaseError) as e:
            # Error de BD: tabla no existe o BD no disponible
            # En modo desarrollo con SQLite, la tabla 'users' no existe
            # Retornamos None para que Django muestre el mensaje de error estándar
            return None

        # Verificar contraseña
        ph = (iu.password_hash or "")
        expected = ph.split("hash_", 1)[-1] if "hash_" in ph else ph
        if not expected or password != expected:
            # Contraseña incorrecta
            return None

        # Crear o actualizar el usuario de Django
        try:
            user, created = User.objects.get_or_create(username=iu.username)
            flags = _role_flags(iu.role)

            if created:
                user.set_unusable_password()
            if flags.get("is_superuser"):
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_staff = user.is_staff or flags.get("is_staff", False)

            user.email = user.email or f"{iu.username}@icesi.edu.co"
            user.is_active = True
            user.save()
            return user
        except Exception:
            # Si hay algún error al crear/actualizar el usuario, retornar None
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
