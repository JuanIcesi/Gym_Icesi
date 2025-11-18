"""
Comando para probar el login y verificar autenticación
Uso: python manage.py test_login
"""
from django.core.management.base import BaseCommand
from fit.auth_backend import InstitutionalBackend
from fit.institutional_models import InstitutionalUser
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Prueba el sistema de autenticación con usuarios de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Probando sistema de autenticacion...\n')
        
        backend = InstitutionalBackend()
        
        # Usuarios de prueba
        test_users = [
            ('laura.h', 'lh123', 'STUDENT'),
            ('paula.r', 'pr123', 'EMPLOYEE - Instructor'),
            ('maria.g', 'mg123', 'EMPLOYEE - Administrativo'),
        ]
        
        # Verificar que los usuarios existen en la BD
        self.stdout.write('1. Verificando usuarios en BD institucional...')
        for username, password, expected_role in test_users:
            try:
                iu = InstitutionalUser.objects.get(username=username)
                self.stdout.write(self.style.SUCCESS(f'  [OK] {username}: Role={iu.role}, Active={iu.is_active}, Password_hash={iu.password_hash}'))
            except InstitutionalUser.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  [ERROR] {username}: NO EXISTE en BD'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] {username}: {e}'))
        
        self.stdout.write('\n2. Probando autenticacion...')
        for username, password, expected_role in test_users:
            self.stdout.write(f'\nProbando: {username} / {password}')
            
            # Simular request
            class FakeRequest:
                pass
            
            request = FakeRequest()
            user = backend.authenticate(request, username=username, password=password)
            
            if user:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Autenticacion exitosa'))
                self.stdout.write(f'     Username: {user.username}')
                self.stdout.write(f'     is_staff: {user.is_staff}')
                self.stdout.write(f'     is_superuser: {user.is_superuser}')
                self.stdout.write(f'     is_active: {user.is_active}')
            else:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Autenticacion fallida'))
                
                # Diagnosticar por qué falló
                try:
                    iu = InstitutionalUser.objects.get(username=username)
                    ph = iu.password_hash or ""
                    expected = ph.split("hash_", 1)[-1] if "hash_" in ph else ph
                    self.stdout.write(f'     Password_hash en BD: {ph}')
                    self.stdout.write(f'     Contraseña esperada: {expected}')
                    self.stdout.write(f'     Contraseña ingresada: {password}')
                    if expected != password:
                        self.stdout.write(self.style.WARNING(f'     [PROBLEMA] Las contraseñas no coinciden'))
                except Exception as e:
                    self.stdout.write(f'     Error al diagnosticar: {e}')

