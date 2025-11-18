"""
Comando de gestión para crear usuarios de prueba en la BD institucional
Uso: python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from django.db import connection
from datetime import datetime


class Command(BaseCommand):
    help = 'Crea usuarios de prueba en la base de datos institucional (tabla users)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando usuarios de prueba...'))
        
        try:
            with connection.cursor() as cursor:
                # Verificar si la tabla users existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    self.stdout.write(self.style.WARNING(
                        'La tabla "users" no existe. Esto es normal si estás usando SQLite.'
                    ))
                    self.stdout.write(self.style.WARNING(
                        'Los usuarios de prueba se crearán en la tabla de Django auth_user.'
                    ))
                    self._create_django_users()
                    return
                
                # Usuarios de prueba
                test_users = [
                    {
                        'username': 'estudiante1',
                        'password_hash': 'hash_estudiante1',
                        'role': 'STUDENT',
                        'student_id': '123456',
                        'employee_id': None,
                        'is_active': True,
                    },
                    {
                        'username': 'entrenador1',
                        'password_hash': 'hash_entrenador1',
                        'role': 'EMPLOYEE',
                        'student_id': None,
                        'employee_id': 'EMP001',
                        'is_active': True,
                    },
                    {
                        'username': 'admin1',
                        'password_hash': 'hash_admin1',
                        'role': 'ADMIN',
                        'student_id': None,
                        'employee_id': None,
                        'is_active': True,
                    },
                ]
                
                created_count = 0
                for user_data in test_users:
                    # Verificar si el usuario ya existe
                    cursor.execute("""
                        SELECT COUNT(*) FROM users WHERE username = %s
                    """, [user_data['username']])
                    
                    exists = cursor.fetchone()[0] > 0
                    
                    if exists:
                        self.stdout.write(
                            self.style.WARNING(f'Usuario {user_data["username"]} ya existe. Saltando...')
                        )
                        continue
                    
                    # Insertar usuario
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role, student_id, employee_id, is_active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [
                        user_data['username'],
                        user_data['password_hash'],
                        user_data['role'],
                        user_data['student_id'],
                        user_data['employee_id'],
                        user_data['is_active'],
                        datetime.now()
                    ])
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Usuario {user_data["username"]} creado ({user_data["role"]})')
                    )
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ {created_count} usuarios creados exitosamente.'
                ))
                self.stdout.write(self.style.SUCCESS('\n📝 Credenciales de prueba:'))
                self.stdout.write(self.style.SUCCESS('  👤 Usuario Estándar:'))
                self.stdout.write(self.style.SUCCESS('     Usuario: estudiante1'))
                self.stdout.write(self.style.SUCCESS('     Contraseña: estudiante1'))
                self.stdout.write(self.style.SUCCESS('  🏋️ Entrenador:'))
                self.stdout.write(self.style.SUCCESS('     Usuario: entrenador1'))
                self.stdout.write(self.style.SUCCESS('     Contraseña: entrenador1'))
                self.stdout.write(self.style.SUCCESS('  ⚙️ Administrador:'))
                self.stdout.write(self.style.SUCCESS('     Usuario: admin1'))
                self.stdout.write(self.style.SUCCESS('     Contraseña: admin1'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            self.stdout.write(self.style.WARNING(
                'Si estás usando SQLite, los usuarios se crearán en Django auth_user.'
            ))
            self._create_django_users()
    
    def _create_django_users(self):
        """Crea usuarios directamente en Django si la BD institucional no está disponible"""
        from django.contrib.auth.models import User
        
        test_users = [
            {'username': 'estudiante1', 'password': 'estudiante1', 'is_staff': False, 'is_superuser': False},
            {'username': 'entrenador1', 'password': 'entrenador1', 'is_staff': True, 'is_superuser': False},
            {'username': 'admin1', 'password': 'admin1', 'is_staff': True, 'is_superuser': True},
        ]
        
        created_count = 0
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Usuario Django {user_data["username"]} creado')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Usuario Django {user_data["username"]} ya existe')
                )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {created_count} usuarios Django creados.'))

