"""
Comando de gestión para insertar datos de prueba en MongoDB
Ejecutar con: python manage.py insert_mongodb_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fit.models import Routine, Exercise, ProgressLog
from fit.mongodb_service import (
    MongoDBService, ProgressLogService, ActivityLogService, 
    ExerciseDetailsService
)
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Inserta datos de prueba en MongoDB para demostrar el funcionamiento'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando inserción de datos en MongoDB...'))
        
        # Verificar conexión
        if not MongoDBService.is_available():
            self.stdout.write(self.style.ERROR('❌ MongoDB no está disponible. Verifica la conexión.'))
            self.stdout.write(self.style.WARNING('El sistema funcionará sin MongoDB, pero no se guardarán datos NoSQL.'))
            return
        
        self.stdout.write(self.style.SUCCESS('✅ Conexión a MongoDB establecida'))
        
        # Obtener usuarios de prueba
        users = User.objects.all()[:5]
        if not users.exists():
            self.stdout.write(self.style.ERROR('No hay usuarios en el sistema. Crea algunos usuarios primero.'))
            return
        
        routines = Routine.objects.all()[:10]
        exercises = Exercise.objects.all()[:10]
        
        if not routines.exists():
            self.stdout.write(self.style.WARNING('No hay rutinas en el sistema. Crea algunas rutinas primero.'))
            return
        
        # 1. Insertar progresos detallados
        self.stdout.write('\n📊 Insertando registros de progreso detallados...')
        progress_count = 0
        for user in users:
            user_routines = routines.filter(user=user)
            if not user_routines.exists():
                continue
            
            for i in range(5):  # 5 registros por usuario
                routine = user_routines.first()
                exercise = exercises.first() if exercises.exists() else None
                fecha = date.today() - timedelta(days=i*2)
                
                try:
                    ProgressLogService.save_detailed_progress(
                        user_id=user.username,
                        routine_id=routine.id,
                        exercise_id=exercise.id if exercise else None,
                        fecha=fecha,
                        series=random.randint(2, 4),
                        reps=random.randint(8, 15),
                        tiempo_seg=random.randint(30, 120),
                        esfuerzo=random.randint(5, 9),
                        notas=f"Entrenamiento del día {fecha.strftime('%d/%m/%Y')}",
                        metricas_adicionales={
                            "ritmo_cardiaco": random.randint(120, 180),
                            "calorias_quemadas": random.randint(150, 400)
                        }
                    )
                    progress_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error insertando progreso: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'✅ {progress_count} registros de progreso insertados'))
        
        # 2. Insertar detalles extendidos de ejercicios
        self.stdout.write('\n💪 Insertando detalles extendidos de ejercicios...')
        exercise_details_count = 0
        for exercise in exercises[:5]:
            try:
                ExerciseDetailsService.save_exercise_details(
                    exercise_id=exercise.id,
                    variaciones=[
                        {
                            "nombre": f"{exercise.nombre} - Variación 1",
                            "descripcion": "Variación más intensa",
                            "video_url": ""
                        }
                    ],
                    consejos=[
                        "Mantén la forma correcta",
                        "Respira adecuadamente",
                        "No sobrecargues el peso"
                    ],
                    equipamiento_necesario=["pesas", "banco"] if exercise.tipo == "fuerza" else ["ninguno"],
                    musculos_trabajados=["cuadriceps", "gluteos"] if exercise.tipo == "fuerza" else ["todo el cuerpo"],
                    nivel_recomendado="intermedio" if exercise.dificultad >= 3 else "principiante",
                    tags=[exercise.tipo, "recomendado"],
                    estadisticas_uso={
                        "veces_usado": random.randint(10, 100),
                        "promedio_series": round(random.uniform(2.5, 4.5), 1),
                        "promedio_reps": random.randint(10, 15)
                    }
                )
                exercise_details_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error insertando detalles de ejercicio: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'✅ {exercise_details_count} detalles de ejercicios insertados'))
        
        # 3. Insertar logs de actividad
        self.stdout.write('\n📝 Insertando logs de actividad...')
        activity_count = 0
        actions = ["create_routine", "add_exercise", "log_progress", "view_report", "adopt_routine"]
        
        for user in users:
            for i, action in enumerate(actions):
                try:
                    ActivityLogService.log_activity(
                        user_id=user.username,
                        action=action,
                        entity_type=action.split("_")[-1],
                        entity_id=i+1,
                        metadata={"test": True, "demo": True}
                    )
                    activity_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error insertando actividad: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'✅ {activity_count} logs de actividad insertados'))
        
        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Inserción de datos completada'))
        self.stdout.write('='*60)
        self.stdout.write(f'📊 Progresos detallados: {progress_count}')
        self.stdout.write(f'💪 Detalles de ejercicios: {exercise_details_count}')
        self.stdout.write(f'📝 Logs de actividad: {activity_count}')
        self.stdout.write('\n💡 Puedes verificar los datos en MongoDB usando MongoDB Compass o la shell de MongoDB')

