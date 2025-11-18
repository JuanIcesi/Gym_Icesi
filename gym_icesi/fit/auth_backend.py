# fit/auth_backend.py
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from django.db import OperationalError, DatabaseError, connection
from .institutional_models import InstitutionalUser

def _role_flags(role: str, employee_id: str = None):
    """
    Determina los flags de usuario según su rol.
    - ADMIN: is_superuser=True, is_staff=True
    - EMPLOYEE con employee_type='Instructor': is_staff=True (entrenador)
    - EMPLOYEE sin employee_type='Instructor': is_staff=False (usuario estándar)
    - STUDENT: is_staff=False (usuario estándar)
    """
    role = (role or "").upper()
    if role == "ADMIN":
        return dict(is_staff=True, is_superuser=True)
    
    if role == "EMPLOYEE" and employee_id:
        # Verificar si es Instructor (entrenador)
        try:
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT employee_type FROM employees WHERE id = %s",
                    [employee_id]
                )
                row = cur.fetchone()
                if row and row[0] and row[0].upper() == "INSTRUCTOR":
                    return dict(is_staff=True, is_superuser=False)  # Es entrenador
        except Exception:
            # Si hay error, asumir que no es entrenador
            pass
    
    # Por defecto: usuario estándar (STUDENT o EMPLOYEE no-instructor)
    return dict(is_staff=False, is_superuser=False)

class InstitutionalBackend(BaseBackend):
    """
    Autentica contra la tabla institucional 'users'.
    Regla demo: password válido = password_hash sin 'hash_'.
    Ej: 'hash_jp123' -> contraseña 'jp123'.
    
    Maneja errores cuando la BD institucional no está disponible (SQLite local).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log del intento de autenticación
        logger.info(f"InstitutionalBackend.authenticate llamado: username={username}, password={'*' * len(password) if password else None}")
        
        if not username or not password:
            logger.warning("Username o password vacíos")
            return None
        
        try:
            # Intentar obtener el usuario de la BD institucional
            iu = InstitutionalUser.objects.get(username=username, is_active=True)
            logger.info(f"Usuario encontrado en BD institucional: {username}, role={iu.role}")
        except InstitutionalUser.DoesNotExist:
            # Usuario no existe en la BD institucional
            logger.warning(f"Usuario no encontrado en BD institucional: {username}")
            return None
        except (OperationalError, DatabaseError) as e:
            # Error de BD: tabla no existe o BD no disponible
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error de BD al autenticar {username}: {e}")
            return None
        except Exception as e:
            # Cualquier otro error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error inesperado al autenticar {username}: {e}")
            return None

        # Verificar contraseña
        ph = (iu.password_hash or "")
        expected = ph.split("hash_", 1)[-1] if "hash_" in ph else ph
        if not expected or password != expected:
            # Contraseña incorrecta
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Contraseña incorrecta para {username}. Esperada: {expected}, Recibida: {password}")
            return None

        # Crear o actualizar el usuario de Django
        try:
            user, created = User.objects.get_or_create(username=iu.username)
            flags = _role_flags(iu.role, iu.employee_id)

            if created:
                user.set_unusable_password()
            
            # Aplicar flags según el rol
            if flags.get("is_superuser"):
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = flags.get("is_staff", False)

            user.email = user.email or f"{iu.username}@icesi.edu.co"
            user.is_active = True
            user.save()
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Usuario autenticado exitosamente: {username} (is_staff={user.is_staff}, is_superuser={user.is_superuser})")
            
            return user
        except Exception as e:
            # Si hay algún error al crear/actualizar el usuario, retornar None
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear/actualizar usuario {username}: {e}")
            logger.error(traceback.format_exc())
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
