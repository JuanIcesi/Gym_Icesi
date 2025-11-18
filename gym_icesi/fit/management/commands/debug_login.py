"""
Comando para debuggear el login en tiempo real
Uso: python manage.py debug_login paula.r pr123
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.test import RequestFactory
from fit.institutional_models import InstitutionalUser
from django.db import connection


class Command(BaseCommand):
    help = 'Debug del login paso a paso'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Usuario a probar')
        parser.add_argument('password', type=str, help='Contraseña a probar')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        self.stdout.write(f'\n=== DEBUG LOGIN: {username} ===\n')
        
        # Paso 1: Verificar que el usuario existe
        self.stdout.write('1. Verificando usuario en BD institucional...')
        try:
            iu = InstitutionalUser.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'   [OK] Usuario encontrado'))
            self.stdout.write(f'   - Role: {iu.role}')
            self.stdout.write(f'   - Password_hash: {iu.password_hash}')
            self.stdout.write(f'   - Employee_id: {iu.employee_id}')
            self.stdout.write(f'   - Is_active: {iu.is_active}')
        except InstitutionalUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'   [ERROR] Usuario NO encontrado'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   [ERROR] {e}'))
            return
        
        # Paso 2: Verificar contraseña
        self.stdout.write('\n2. Verificando contraseña...')
        ph = iu.password_hash or ""
        expected = ph.split("hash_", 1)[-1] if "hash_" in ph else ph
        self.stdout.write(f'   - Password_hash en BD: {ph}')
        self.stdout.write(f'   - Contraseña esperada: {expected}')
        self.stdout.write(f'   - Contraseña recibida: {password}')
        if expected == password:
            self.stdout.write(self.style.SUCCESS(f'   [OK] Contraseña correcta'))
        else:
            self.stdout.write(self.style.ERROR(f'   [ERROR] Contraseña NO coincide'))
            return
        
        # Paso 3: Verificar employee_type si es empleado
        if iu.role == 'EMPLOYEE' and iu.employee_id:
            self.stdout.write('\n3. Verificando tipo de empleado...')
            try:
                with connection.cursor() as cur:
                    cur.execute(
                        "SELECT employee_type FROM employees WHERE id = %s",
                        [iu.employee_id]
                    )
                    row = cur.fetchone()
                    if row:
                        emp_type = row[0]
                        self.stdout.write(f'   - Employee_type: {emp_type}')
                        if emp_type and emp_type.upper() == "INSTRUCTOR":
                            self.stdout.write(self.style.SUCCESS(f'   [OK] Es Instructor (entrenador)'))
                        else:
                            self.stdout.write(f'   [INFO] NO es Instructor (usuario estándar)')
                    else:
                        self.stdout.write(self.style.WARNING(f'   [WARNING] No se encontró el empleado'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   [ERROR] {e}'))
        
        # Paso 4: Probar autenticación completa
        self.stdout.write('\n4. Probando autenticación completa...')
        rf = RequestFactory()
        request = rf.post('/login/')
        user = authenticate(request, username=username, password=password)
        
        if user:
            self.stdout.write(self.style.SUCCESS(f'   [OK] Autenticación exitosa'))
            self.stdout.write(f'   - Username: {user.username}')
            self.stdout.write(f'   - is_staff: {user.is_staff}')
            self.stdout.write(f'   - is_superuser: {user.is_superuser}')
            self.stdout.write(f'   - is_active: {user.is_active}')
        else:
            self.stdout.write(self.style.ERROR(f'   [ERROR] Autenticación fallida'))
            self.stdout.write(f'   Revisa los logs del servidor para más detalles')

