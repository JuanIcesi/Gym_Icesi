"""
Script para demostrar el uso de MongoDB en la aplicación Gym Icesi
Este script muestra cómo se están usando las colecciones de MongoDB
y permite insertar datos de ejemplo para sustentar ante el profesor
"""
import os
import sys
import django
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.contrib.auth.models import User
from fit.models import Routine, ProgressLog, Exercise
from fit.mongodb_service import (
    ProgressLogService,
    ActivityLogService,
    ExerciseDetailsService,
    ExerciseService,
    RoutineService
)

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"[OK] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def print_section(text):
    print(f"\n{'-'*70}")
    print(f"  {text}")
    print(f"{'-'*70}")

def demostrar_progress_logs():
    """Demuestra el uso de ProgressLogService"""
    print_section("1. PROGRESS LOGS (Registros de Progreso Detallados)")
    
    # Obtener un usuario y rutina de ejemplo
    user = User.objects.first()
    routine = Routine.objects.first()
    
    if not user or not routine:
        print_info("No hay usuarios o rutinas en la BD. Creando datos de ejemplo...")
        if not user:
            user = User.objects.create_user(username='demo_user', password='demo123')
        if not routine:
            routine = Routine.objects.create(
                nombre='Rutina Demo',
                user=user
            )
    
    print_info(f"Usuario: {user.username}")
    print_info(f"Rutina: {routine.nombre}")
    
    # Crear un registro de progreso en PostgreSQL
    progress_log = ProgressLog.objects.create(
        user=user,
        routine=routine,
        fecha=date.today(),
        tiempo_seg=1800,
        esfuerzo=8,
        repeticiones=50,
        peso_usado=20.5,
        notas="Excelente sesión, me sentí muy bien"
    )
    
    print_info(f"Registro de progreso creado en PostgreSQL (ID: {progress_log.id})")
    
    # Guardar detalles extendidos en MongoDB
    detalles_mongo = {
        "ejercicios_detallados": [
            {
                "ejercicio": "Sentadillas",
                "series_completadas": 3,
                "repeticiones_planificadas": 10,
                "repeticiones_realizadas": 12,
                "peso_kg": 20.5,
                "tiempo_seg": 45,
                "esfuerzo_percibido": 8,
                "notas": "Buenas repeticiones, forma correcta"
            },
            {
                "ejercicio": "Press de banca",
                "series_completadas": 3,
                "repeticiones_planificadas": 8,
                "repeticiones_realizadas": 8,
                "peso_kg": 40.0,
                "tiempo_seg": 60,
                "esfuerzo_percibido": 7,
                "notas": "Mantengo el peso estable"
            }
        ],
        "metricas_fisicas": {
            "frecuencia_cardiaca_promedio": 145,
            "frecuencia_cardiaca_maxima": 165,
            "calorias_quemadas": 320,
            "distancia_recorrida_km": 0,
            "elevacion_metros": 0
        },
        "sensaciones": {
            "nivel_energia": 8,
            "nivel_motivacion": 9,
            "dolor_muscular": 2,
            "comentarios": "Me sentí muy energético hoy"
        },
        "condiciones_ambientales": {
            "temperatura_c": 22,
            "humedad_porcentaje": 60,
            "lugar": "Gimnasio Principal"
        },
        "tags": ["fuerza", "piernas", "pecho", "buena_sesion"],
        "fecha_creacion": datetime.now().isoformat()
    }
    
    try:
        # Guardar en MongoDB usando la firma correcta del servicio
        mongo_id = ProgressLogService.save_detailed_progress(
            user_id=user.username,
            routine_id=routine.id,
            exercise_id=None,  # Se puede obtener del primer item si existe
            fecha=progress_log.fecha,
            series=3,
            reps=50,
            tiempo_seg=1800,
            esfuerzo=8,
            peso_usado=20.5,
            notas="Excelente sesion, me senti muy bien",
            metricas_adicionales=detalles_mongo
        )
        print_success(f"Detalles guardados en MongoDB (ID: {mongo_id})")
        
        # Recuperar y mostrar
        detalles_recuperados = ProgressLogService.get_user_progress(
            user_id=user.username,
            limit=1
        )
        if detalles_recuperados:
            print_success("Datos recuperados de MongoDB:")
            primer_log = detalles_recuperados[0]
            print_info(f"  - Tiempo segundos: {primer_log.get('tiempo_segundos', 'N/A')}")
            print_info(f"  - Esfuerzo: {primer_log.get('esfuerzo_percibido', 'N/A')}")
            print_info(f"  - Notas: {primer_log.get('notas', 'N/A')}")
            print_info(f"  - Metricas adicionales: {bool(primer_log.get('metricas_adicionales', {}))}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar en MongoDB: {e}")
        return False

def demostrar_activity_logs():
    """Demuestra el uso de ActivityLogService"""
    print_section("2. ACTIVITY LOGS (Logs de Actividad del Sistema)")
    
    user = User.objects.first()
    if not user:
        return False
    
    try:
        # Registrar algunas actividades
        actividades = [
            {
                "accion": "crear_rutina",
                "detalles": {"rutina_id": 1, "nombre": "Rutina Nueva"},
                "timestamp": datetime.now()
            },
            {
                "accion": "registrar_progreso",
                "detalles": {"progress_id": 1, "tiempo_seg": 1800},
                "timestamp": datetime.now()
            },
            {
                "accion": "ver_ejercicio",
                "detalles": {"exercise_id": 1, "nombre": "Sentadillas"},
                "timestamp": datetime.now()
            }
        ]
        
        for actividad in actividades:
            log_id = ActivityLogService.log_activity(
                user_id=user.username,
                action=actividad["accion"],
                entity_type=actividad["detalles"].get("tipo", None),
                entity_id=actividad["detalles"].get("id", None),
                metadata=actividad["detalles"]
            )
            print_success(f"Actividad '{actividad['accion']}' registrada (ID: {log_id})")
        
        # Verificar que se guardaron
        from fit.mongodb_service import MongoDBService
        db = MongoDBService.get_db()
        if db:
            count = db.user_activity_logs.count_documents({"user_id": str(user.username)})
            print_success(f"Total de logs de actividad para {user.username}: {count}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error con Activity Logs: {e}")
        return False

def demostrar_exercise_details():
    """Demuestra el uso de ExerciseDetailsService"""
    print_section("3. EXERCISE DETAILS (Detalles Extendidos de Ejercicios)")
    
    exercise = Exercise.objects.first()
    if not exercise:
        exercise = Exercise.objects.create(
            nombre="Sentadillas",
            tipo="fuerza",
            descripcion="Ejercicio básico",
            duracion_min=10,
            dificultad=3
        )
    
    try:
        detalles = {
            "estadisticas_uso": {
                "veces_realizado": 45,
                "usuarios_que_lo_usan": 12,
                "promedio_repeticiones": 10.5,
                "promedio_peso_kg": 18.3
            },
            "variaciones_populares": [
                {"nombre": "Sentadillas con peso", "uso_porcentaje": 60},
                {"nombre": "Sentadillas libres", "uso_porcentaje": 40}
            ],
            "comentarios_usuarios": [
                {"usuario": "laura.h", "comentario": "Excelente ejercicio", "rating": 5},
                {"usuario": "carlos.m", "comentario": "Muy efectivo", "rating": 4}
            ],
            "tags_populares": ["piernas", "fuerza", "básico", "efectivo"],
            "fecha_ultima_actualizacion": datetime.now().isoformat()
        }
        
        detail_id = ExerciseDetailsService.save_exercise_details(
            exercise_id=exercise.id,
            details=detalles
        )
        print_success(f"Detalles del ejercicio guardados (ID: {detail_id})")
        
        # Recuperar
        detalles_recuperados = ExerciseDetailsService.get_exercise_details(exercise.id)
        if detalles_recuperados:
            print_success("Detalles recuperados:")
            print_info(f"  - Veces realizado: {detalles_recuperados.get('estadisticas_uso', {}).get('veces_realizado', 0)}")
            print_info(f"  - Usuarios que lo usan: {detalles_recuperados.get('estadisticas_uso', {}).get('usuarios_que_lo_usan', 0)}")
            print_info(f"  - Tags: {detalles_recuperados.get('tags_populares', [])}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error con Exercise Details: {e}")
        return False

def mostrar_colecciones_mongodb():
    """Muestra todas las colecciones y sus documentos"""
    print_section("4. COLECCIONES EN MONGODB")
    
    try:
        from fit.mongodb_service import MongoDBService
        db = MongoDBService.get_db()
        
        if db is None:
            print("[ERROR] No se pudo conectar a MongoDB")
            return False
        
        colecciones = db.list_collection_names()
        print_info(f"Colecciones encontradas: {len(colecciones)}")
        
        for coleccion_nombre in colecciones:
            coleccion = db[coleccion_nombre]
            count = coleccion.count_documents({})
            print_info(f"\n📁 Colección: {coleccion_nombre}")
            print_info(f"   Documentos: {count}")
            
            if count > 0:
                # Mostrar un ejemplo
                ejemplo = coleccion.find_one()
                if ejemplo:
                    print_info(f"   Ejemplo de campos: {list(ejemplo.keys())[:5]}...")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error al mostrar colecciones: {e}")
        return False

def mostrar_justificacion():
    """Muestra la justificación del uso de MongoDB"""
    print_section("5. JUSTIFICACIÓN DEL USO DE MONGODB")
    
    justificacion = """
    ¿Por qué MongoDB para Gym Icesi?
    
    1. FLEXIBILIDAD DE ESQUEMA:
       - Los registros de progreso pueden tener diferentes estructuras
       - Cada usuario puede agregar métricas personalizadas
       - No requiere migraciones cuando se agregan nuevos campos
    
    2. DATOS SEMI-ESTRUCTURADOS:
       - Ejercicios detallados con variaciones
       - Logs de actividad con diferentes formatos
       - Métricas físicas que pueden variar por tipo de ejercicio
    
    3. ESCALABILIDAD:
       - MongoDB maneja grandes volúmenes de datos de progreso
       - Consultas rápidas sobre documentos JSON
       - Ideal para datos que crecen constantemente
    
    4. SEPARACIÓN DE CONCERNS:
       - PostgreSQL: Datos estructurados (usuarios, rutinas, relaciones)
       - MongoDB: Datos flexibles (progreso detallado, logs, metadata)
    
    5. RENDIMIENTO:
       - Consultas rápidas sobre documentos completos
       - No requiere JOINs complejos
       - Indexación eficiente de campos anidados
    """
    
    print(justificacion)

def main():
    print_header("DEMOSTRACIÓN DE USO DE MONGODB - GYM ICESI")
    
    print_info("Este script demuestra cómo se está usando MongoDB en la aplicación")
    print_info("para almacenar datos flexibles y detallados que complementan PostgreSQL")
    
    resultados = {
        'progress_logs': False,
        'activity_logs': False,
        'exercise_details': False,
        'colecciones': False
    }
    
    # Demostrar cada funcionalidad
    resultados['progress_logs'] = demostrar_progress_logs()
    resultados['activity_logs'] = demostrar_activity_logs()
    resultados['exercise_details'] = demostrar_exercise_details()
    resultados['colecciones'] = mostrar_colecciones_mongodb()
    
    # Mostrar justificación
    mostrar_justificacion()
    
    # Resumen
    print_header("RESUMEN")
    
    print("\nFuncionalidades demostradas:")
    print(f"  Progress Logs: {'OK' if resultados['progress_logs'] else 'ERROR'}")
    print(f"  Activity Logs: {'OK' if resultados['activity_logs'] else 'ERROR'}")
    print(f"  Exercise Details: {'OK' if resultados['exercise_details'] else 'ERROR'}")
    print(f"  Colecciones: {'OK' if resultados['colecciones'] else 'ERROR'}")
    
    print("\n" + "="*70)
    print("PARA SUSTENTAR ANTE TU PROFESOR:")
    print("="*70)
    print("1. Ejecuta este script: python demostrar_mongodb.py")
    print("2. Muestra las colecciones creadas en MongoDB Atlas")
    print("3. Explica que:")
    print("   - PostgreSQL guarda datos estructurados (relaciones)")
    print("   - MongoDB guarda datos flexibles (progreso detallado, logs)")
    print("   - Ambos trabajan juntos para un sistema completo")
    print("4. Muestra ejemplos de documentos en MongoDB Atlas")
    print("5. Compara con los datos en PostgreSQL para mostrar la diferencia")
    print("="*70)
    
    return all(resultados.values())

if __name__ == '__main__':
    try:
        exit_code = 0 if main() else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDemostración interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

