"""
Comando para configurar completamente la base de datos relacional
Incluye: verificación, creación de esquema, y datos de prueba
Uso: python manage.py setup_database
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection, transaction
from django.contrib.auth.models import User
from fit.models import (
    Exercise, Routine, RoutineItem, ProgressLog,
    TrainerAssignment, UserMonthlyStats, TrainerMonthlyStats,
    TrainerRecommendation
)
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Configura completamente la base de datos: verifica conexión, crea esquema y datos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Omitir ejecución de migraciones',
        )
        parser.add_argument(
            '--skip-test-data',
            action='store_true',
            help='Omitir creación de datos de prueba',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('  CONFIGURACION COMPLETA DE BASE DE DATOS'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        # Paso 1: Verificar conexión
        if not self._verify_connection():
            self.stdout.write(self.style.ERROR('\n[ERROR] No se pudo conectar a la base de datos'))
            self.stdout.write(self.style.WARNING('[TIP] Verifica las credenciales en .env'))
            return
        
        # Paso 2: Aplicar migraciones
        if not options['skip_migrations']:
            self._run_migrations()
        else:
            self.stdout.write(self.style.WARNING('\n[SKIP] Migraciones omitidas'))
        
        # Paso 3: Verificar tablas
        self._verify_tables()
        
        # Paso 4: Crear datos de prueba
        if not options['skip_test_data']:
            self._create_test_data()
        else:
            self.stdout.write(self.style.WARNING('\n[SKIP] Datos de prueba omitidos'))
        
        # Paso 5: Resumen final
        self._show_summary()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('  CONFIGURACION COMPLETADA EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('='*70))

    def _verify_connection(self):
        """Verifica la conexión a la base de datos"""
        self.stdout.write('\n[1/5] Verificando conexion a la base de datos...')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'  [OK] Conexion exitosa'))
                self.stdout.write(f'  PostgreSQL: {version.split(",")[0]}')
                return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] {e}'))
            return False

    def _run_migrations(self):
        """Ejecuta las migraciones de Django"""
        self.stdout.write('\n[2/5] Aplicando migraciones...')
        
        try:
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  [OK] Migraciones aplicadas correctamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] {e}'))
            raise

    def _verify_tables(self):
        """Verifica que todas las tablas necesarias existan"""
        self.stdout.write('\n[3/5] Verificando tablas...')
        
        required_tables = [
            ('fit_exercise', 'Ejercicios'),
            ('fit_routine', 'Rutinas'),
            ('fit_routineitem', 'Items de Rutina'),
            ('fit_progresslog', 'Logs de Progreso'),
            ('fit_trainerassignment', 'Asignaciones de Entrenador'),
            ('fit_trainerrecommendation', 'Recomendaciones'),
            ('fit_usermonthlystats', 'Estadísticas Mensuales Usuario'),
            ('fit_trainermonthlystats', 'Estadísticas Mensuales Entrenador'),
        ]
        
        all_exist = True
        with connection.cursor() as cursor:
            for table_name, description in required_tables:
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    );
                """)
                exists = cursor.fetchone()[0]
                
                if exists:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    self.stdout.write(self.style.SUCCESS(f'  [OK] {description}: {count} registros'))
                else:
                    self.stdout.write(self.style.ERROR(f'  [ERROR] {description}: NO EXISTE'))
                    all_exist = False
        
        if not all_exist:
            self.stdout.write(self.style.WARNING('  [TIP] Ejecuta: python manage.py migrate'))
        
        return all_exist

    def _create_test_data(self):
        """Crea datos de prueba para la aplicación"""
        self.stdout.write('\n[4/5] Creando datos de prueba...')
        
        try:
            with transaction.atomic():
                # Obtener usuarios institucionales existentes
                users = User.objects.all()[:5]
                if not users.exists():
                    self.stdout.write(self.style.WARNING('  [WARNING] No hay usuarios en la BD'))
                    self.stdout.write(self.style.WARNING('  [TIP] Asegurate de haber cargado university_full_data_postgresql.sql'))
                    return
                
                # 1. Crear ejercicios si no existen
                if Exercise.objects.count() == 0:
                    self.stdout.write('  Creando ejercicios...')
                    exercises_data = [
                        {'nombre': 'Sentadillas', 'tipo': 'fuerza', 'dificultad': 2},
                        {'nombre': 'Flexiones', 'tipo': 'fuerza', 'dificultad': 3},
                        {'nombre': 'Correr', 'tipo': 'cardio', 'dificultad': 2},
                        {'nombre': 'Plancha', 'tipo': 'fuerza', 'dificultad': 3},
                        {'nombre': 'Estiramiento', 'tipo': 'movilidad', 'dificultad': 1},
                    ]
                    for ex_data in exercises_data:
                        Exercise.objects.get_or_create(
                            nombre=ex_data['nombre'],
                            defaults={
                                'tipo': ex_data['tipo'],
                                'dificultad': ex_data['dificultad'],
                                'descripcion': f'Ejercicio de {ex_data["tipo"]}',
                                'duracion_min': 10 if ex_data['tipo'] == 'cardio' else 0,
                            }
                        )
                    self.stdout.write(self.style.SUCCESS(f'    [OK] {Exercise.objects.count()} ejercicios creados'))
                
                # 2. Crear rutinas de prueba
                self.stdout.write('  Creando rutinas...')
                routines_created = 0
                exercises = list(Exercise.objects.all())
                
                for user in users:
                    if Routine.objects.filter(user=user).count() == 0:
                        routine = Routine.objects.create(
                            user=user,
                            nombre=f'Rutina de {user.username}',
                            descripcion='Rutina de prueba creada automáticamente',
                            es_predisenada=False
                        )
                        
                        # Agregar ejercicios a la rutina
                        for i, exercise in enumerate(exercises[:3], 1):
                            RoutineItem.objects.create(
                                routine=routine,
                                exercise=exercise,
                                orden=i,
                                series=3,
                                reps=10 if exercise.tipo == 'fuerza' else None,
                                tiempo_seg=30 if exercise.tipo == 'cardio' else None,
                            )
                        routines_created += 1
                
                if routines_created > 0:
                    self.stdout.write(self.style.SUCCESS(f'    [OK] {routines_created} rutinas creadas'))
                
                # 3. Crear registros de progreso
                self.stdout.write('  Creando registros de progreso...')
                progress_created = 0
                routines = list(Routine.objects.all())
                
                for user in users:
                    user_routines = [r for r in routines if r.user == user]
                    if user_routines:
                        # Crear 3-5 registros de progreso en los últimos 30 días
                        for i in range(random.randint(3, 5)):
                            routine = random.choice(user_routines)
                            fecha = date.today() - timedelta(days=random.randint(1, 30))
                            
                            ProgressLog.objects.get_or_create(
                                user=user,
                                routine=routine,
                                fecha=fecha,
                                defaults={
                                    'repeticiones': random.randint(20, 50) if routine.items.filter(reps__isnull=False).exists() else None,
                                    'tiempo_seg': random.randint(600, 1800) if routine.items.filter(tiempo_seg__isnull=False).exists() else None,
                                    'esfuerzo': random.randint(5, 9),
                                    'notas': f'Sesión de prueba {i+1}',
                                }
                            )
                            progress_created += 1
                
                if progress_created > 0:
                    self.stdout.write(self.style.SUCCESS(f'    [OK] {progress_created} registros de progreso creados'))
                
                # 4. Crear asignaciones de entrenador (si hay entrenadores)
                trainers = [u for u in users if u.is_staff and not u.is_superuser]
                regular_users = [u for u in users if not u.is_staff and not u.is_superuser]
                
                if trainers and regular_users:
                    self.stdout.write('  Creando asignaciones de entrenador...')
                    assignments_created = 0
                    
                    for user in regular_users[:3]:  # Asignar a máximo 3 usuarios
                        trainer = random.choice(trainers)
                        TrainerAssignment.objects.get_or_create(
                            user=user,
                            trainer=trainer,
                            activo=True,
                            defaults={'fecha_asignacion': date.today() - timedelta(days=random.randint(1, 60))}
                        )
                        assignments_created += 1
                    
                    if assignments_created > 0:
                        self.stdout.write(self.style.SUCCESS(f'    [OK] {assignments_created} asignaciones creadas'))
                
                # 5. Las estadísticas se actualizarán automáticamente mediante señales
                self.stdout.write(self.style.SUCCESS('  [OK] Datos de prueba creados correctamente'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
            raise

    def _show_summary(self):
        """Muestra un resumen de la configuración"""
        self.stdout.write('\n[5/5] Resumen de la base de datos:')
        
        with connection.cursor() as cursor:
            # Contar registros en cada tabla
            tables = {
                'fit_exercise': 'Ejercicios',
                'fit_routine': 'Rutinas',
                'fit_routineitem': 'Items de Rutina',
                'fit_progresslog': 'Registros de Progreso',
                'fit_trainerassignment': 'Asignaciones',
                'fit_trainerrecommendation': 'Recomendaciones',
                'fit_usermonthlystats': 'Stats Usuario',
                'fit_trainermonthlystats': 'Stats Entrenador',
            }
            
            for table, name in tables.items():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'  {name}: {count} registros')
                except:
                    self.stdout.write(f'  {name}: N/A')
        
        self.stdout.write('\n[INFO] La base de datos esta lista para usar!')
        self.stdout.write('[INFO] Puedes iniciar sesion con los usuarios institucionales')

