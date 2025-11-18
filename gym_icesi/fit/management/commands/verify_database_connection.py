"""
Comando para verificar la conexión y configuración de las bases de datos
Uso: python manage.py verify_database_connection
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica la conexión a Neon PostgreSQL y las tablas institucionales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Verificando configuracion de bases de datos...\n'))
        
        # Verificar configuración de PostgreSQL
        self._verify_postgresql()
        
        # Verificar tablas institucionales
        self._verify_institutional_tables()
        
        # Verificar tablas de la aplicación
        self._verify_app_tables()
        
        # Verificar usuarios de prueba
        self._verify_test_users()
        
        self.stdout.write(self.style.SUCCESS('\nVerificacion completada!'))
    
    def _verify_postgresql(self):
        """Verifica la conexión a PostgreSQL"""
        self.stdout.write('Verificando conexion a PostgreSQL...')
        
        try:
            db_config = settings.DATABASES['default']
            engine = db_config['ENGINE']
            
            if 'sqlite' in engine:
                self.stdout.write(self.style.WARNING('  [WARNING] Usando SQLite (modo desarrollo)'))
                self.stdout.write(self.style.WARNING('  [WARNING] Las tablas institucionales no estaran disponibles'))
                return False
            
            if 'postgresql' not in engine:
                self.stdout.write(self.style.ERROR('  [ERROR] Motor de BD no reconocido'))
                return False
            
            self.stdout.write(self.style.SUCCESS('  [OK] Motor: PostgreSQL'))
            self.stdout.write(f'  Host: {db_config.get("HOST", "N/A")}')
            self.stdout.write(f'  Database: {db_config.get("NAME", "N/A")}')
            self.stdout.write(f'  User: {db_config.get("USER", "N/A")}')
            
            # Intentar conexión
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'  [OK] Conexion exitosa'))
                self.stdout.write(f'  Version: {version[:50]}...')
            
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error de conexion: {e}'))
            self.stdout.write(self.style.WARNING('  [TIP] Verifica las credenciales en .env'))
            return False
    
    def _verify_institutional_tables(self):
        """Verifica que las tablas institucionales existan"""
        self.stdout.write('\nVerificando tablas institucionales...')
        
        required_tables = [
            'users', 'students', 'employees', 'faculties', 
            'campuses', 'cities', 'departments', 'countries'
        ]
        
        try:
            with connection.cursor() as cursor:
                for table in required_tables:
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        );
                    """)
                    exists = cursor.fetchone()[0]
                    
                    if exists:
                        # Contar registros
                        cursor.execute(f"SELECT COUNT(*) FROM {table};")
                        count = cursor.fetchone()[0]
                        self.stdout.write(self.style.SUCCESS(f'  [OK] {table}: {count} registros'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  [ERROR] {table}: NO EXISTE'))
                        self.stdout.write(self.style.WARNING(f'     [TIP] Ejecuta university_schema_postgresql.sql'))
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error verificando tablas: {e}'))
    
    def _verify_app_tables(self):
        """Verifica que las tablas de la aplicación existan"""
        self.stdout.write('\nVerificando tablas de la aplicacion...')
        
        required_tables = [
            'fit_exercise', 'fit_routine', 'fit_routineitem',
            'fit_progresslog', 'fit_trainerassignment',
            'fit_trainerrecommendation', 'fit_usermonthlystats',
            'fit_trainermonthlystats'
        ]
        
        try:
            with connection.cursor() as cursor:
                for table in required_tables:
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        );
                    """)
                    exists = cursor.fetchone()[0]
                    
                    if exists:
                        cursor.execute(f"SELECT COUNT(*) FROM {table};")
                        count = cursor.fetchone()[0]
                        self.stdout.write(self.style.SUCCESS(f'  [OK] {table}: {count} registros'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  [WARNING] {table}: NO EXISTE'))
                        self.stdout.write(self.style.WARNING(f'     [TIP] Ejecuta: python manage.py migrate'))
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error verificando tablas: {e}'))
    
    def _verify_test_users(self):
        """Verifica que existan usuarios de prueba"""
        self.stdout.write('\nVerificando usuarios de prueba...')
        
        # Usuarios de prueba que vienen en university_full_data_postgresql.sql
        test_users = ['laura.h', 'paula.r', 'maria.g']
        
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
                    self.stdout.write(self.style.WARNING('  [WARNING] Tabla USERS no existe'))
                    self.stdout.write(self.style.WARNING('     [TIP] Ejecuta university_schema_postgresql.sql'))
                    return
                
                for username in test_users:
                    cursor.execute("""
                        SELECT username, role, student_id, employee_id, is_active 
                        FROM users 
                        WHERE username = %s
                    """, [username])
                    user = cursor.fetchone()
                    
                    if user:
                        role_info = f"Role: {user[1]}"
                        if user[2]:
                            role_info += f" | Student: {user[2]}"
                        if user[3]:
                            role_info += f" | Employee: {user[3]}"
                        status = "[ACTIVO]" if user[4] else "[INACTIVO]"
                        self.stdout.write(self.style.SUCCESS(f'  [OK] {username}: {role_info} | {status}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  [WARNING] {username}: NO EXISTE'))
                        self.stdout.write(self.style.WARNING(f'     [TIP] Ejecuta university_full_data_postgresql.sql'))
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error verificando usuarios: {e}'))

