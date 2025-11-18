# fit/auth_views.py
"""
Vistas personalizadas de autenticación
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django import forms
from django.shortcuts import redirect
from django.db import connection

class CustomLoginView(LoginView):
    """
    Vista de login personalizada que valida el rol del usuario
    según el tipo de login seleccionado
    """
    template_name = "auth/login.html"
    
    def get_context_data(self, **kwargs):
        """Agregar información del rol esperado al contexto"""
        context = super().get_context_data(**kwargs)
        role = self.request.GET.get('role', 'user')
        context['expected_role'] = role
        context['role_name'] = {
            'user': 'Usuario Estándar',
            'trainer': 'Entrenador',
            'admin': 'Administrador'
        }.get(role, 'Usuario Estándar')
        return context
    
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
    
    def _validate_user_role(self, username, expected_role):
        """
        Valida que el usuario tenga el rol correcto para el tipo de login
        """
        try:
            with connection.cursor() as cursor:
                # Obtener información del usuario institucional
                cursor.execute("""
                    SELECT role, student_id, employee_id 
                    FROM users 
                    WHERE username = %s AND is_active = TRUE
                """, [username])
                row = cursor.fetchone()
                
                if not row:
                    return False, "Usuario no encontrado"
                
                role, student_id, employee_id = row
                role = (role or "").upper()
                
                # Validar según el rol esperado
                if expected_role == 'user':
                    # Usuario estándar: estudiantes (STUDENT) y empleados que NO son Instructores ni Administrativos
                    if role == 'STUDENT':
                        return True, None
                    elif role == 'EMPLOYEE' and employee_id:
                        # Verificar que NO sea Instructor ni Administrativo
                        cursor.execute("""
                            SELECT employee_type 
                            FROM employees 
                            WHERE id = %s
                        """, [employee_id])
                        emp_row = cursor.fetchone()
                        
                        if emp_row:
                            emp_type = (emp_row[0] or "").upper()
                            # Permitir si es Docente u otro tipo que no sea Instructor ni Administrativo
                            if emp_type not in ['INSTRUCTOR', 'ADMINISTRATIVO']:
                                return True, None
                            else:
                                if emp_type == 'INSTRUCTOR':
                                    return False, "Este login es para estudiantes y colaboradores. Si eres entrenador, usa el login de Entrenador."
                                else:
                                    return False, "Este login es para estudiantes y colaboradores. Si eres administrador, usa el login de Administrador."
                    
                    return False, "Este login es solo para estudiantes y colaboradores. Si eres entrenador o administrador, usa el login correspondiente."
                
                elif expected_role == 'trainer':
                    # Entrenador: cualquier empleado (EMPLOYEE) puede ser entrenador
                    if role != 'EMPLOYEE' or not employee_id:
                        return False, "Este login es solo para entrenadores (empleados). Si eres estudiante, usa el login de Usuario Estándar."
                    
                    # Verificar que el empleado exista
                    cursor.execute("""
                        SELECT employee_type 
                        FROM employees 
                        WHERE id = %s
                    """, [employee_id])
                    emp_row = cursor.fetchone()
                    
                    if not emp_row:
                        return False, "Empleado no encontrado en la base de datos."
                    
                    # Cualquier empleado puede ser entrenador
                    return True, None
                
                elif expected_role == 'admin':
                    # Administrador: solo empleados con role='ADMIN' o employee_type='Administrativo' con permisos especiales
                    # Por ahora, verificamos si es ADMIN en la tabla users
                    # Si no hay usuarios ADMIN, podemos usar empleados administrativos como alternativa
                    if role == 'ADMIN':
                        return True, None
                    elif role == 'EMPLOYEE' and employee_id:
                        # Verificar si es administrativo (puede ser admin del sistema)
                        cursor.execute("""
                            SELECT employee_type 
                            FROM employees 
                            WHERE id = %s
                        """, [employee_id])
                        emp_row = cursor.fetchone()
                        
                        if emp_row and (emp_row[0] or "").upper() == 'ADMINISTRATIVO':
                            # Permitir acceso a administrativos como admin (si no hay usuarios ADMIN)
                            return True, None
                    
                    return False, "Este login es solo para administradores. Si eres estudiante o entrenador, usa el login correspondiente."
                
                return False, "Rol no reconocido"
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error validando rol: {e}")
            return False, "Error al validar el rol del usuario"
    
    def form_valid(self, form):
        """
        Cuando el formulario es válido, validar rol y autenticar
        """
        import logging
        logger = logging.getLogger(__name__)
        
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        # Obtener el rol desde GET (URL) o POST (formulario)
        expected_role = self.request.GET.get('role') or self.request.POST.get('expected_role', 'user')
        
        logger.info(f"CustomLoginView.form_valid: usuario={username}, rol_esperado={expected_role}")
        
        # Validar que el usuario tenga el rol correcto
        role_valid, error_message = self._validate_user_role(username, expected_role)
        
        if not role_valid:
            logger.warning(f"Rol incorrecto para {username}: {error_message}")
            messages.error(
                self.request,
                error_message,
                extra_tags="login_error"
            )
            return self.form_invalid(form)
        
        # Autenticar manualmente para asegurar que use nuestro backend
        user = authenticate(
            request=self.request,
            username=username,
            password=password,
            expected_role=expected_role  # Pasar el rol esperado al backend
        )
        
        if user is not None:
            if user.is_active:
                login(self.request, user)
                logger.info(f"Login exitoso para: {username} (rol: {expected_role})")
                return redirect(self.get_success_url())
            else:
                logger.warning(f"Usuario inactivo: {username}")
                messages.error(self.request, "Esta cuenta está inactiva.")
                return self.form_invalid(form)
        else:
            logger.warning(f"Autenticación fallida para: {username}")
            messages.error(
                self.request,
                "Las credenciales ingresadas son incorrectas. Por favor, verifica tu usuario y contraseña.",
                extra_tags="login_error"
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """
        Cuando el formulario es inválido (credenciales incorrectas),
        mostrar un mensaje claro al usuario
        """
        import logging
        logger = logging.getLogger(__name__)
        
        username = form.data.get('username', 'N/A')
        logger.warning(f"Login fallido para usuario: {username}")
        
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

