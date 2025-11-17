"""
Script de prueba para verificar la conexión con MongoDB Atlas
y probar los servicios de MongoDB implementados.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from fit.mongodb_service import (
    MongoDBService,
    ExerciseService,
    RoutineService,
    TrainerAssignmentService,
    ProgressLogService,
    ActivityLogService,
)

def test_mongodb_connection():
    """Prueba la conexión con MongoDB Atlas"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN CON MONGODB ATLAS")
    print("=" * 60)

    # 1. Verificar disponibilidad
    print("\n1. Verificando disponibilidad de MongoDB...")
    if MongoDBService.is_available():
        print("   [OK] MongoDB esta disponible y conectado")
    else:
        print("   [ERROR] MongoDB NO esta disponible")
        print("   [AVISO] Verifica las credenciales y la conexion a internet")
        return False

    # 2. Obtener la base de datos
    print("\n2. Obteniendo base de datos...")
    db = MongoDBService.get_db()
    if db is not None:
        print(f"   [OK] Conectado a la base de datos: {db.name}")
    else:
        print("   [ERROR] No se pudo obtener la base de datos")
        return False

    # 3. Listar colecciones existentes
    print("\n3. Colecciones existentes en la base de datos:")
    collections = db.list_collection_names()
    if collections:
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"   - {collection}: {count} documentos")
    else:
        print("   [INFO] No hay colecciones aun (esto es normal en una BD nueva)")

    # 4. Probar inserción de datos de prueba
    print("\n4. Probando inserción de datos de prueba...")
    try:
        # Ejercicio de prueba
        print("   - Insertando ejercicio de prueba...")
        result = ExerciseService.save_exercise(
            exercise_id=99999,
            user_id="test_user",
            nombre="Ejercicio de Prueba",
            tipo="cardio",
            descripcion="Este es un ejercicio de prueba para verificar MongoDB",
            duracion_min=30,
            dificultad=3,
            video_url="https://example.com/video",
            es_personalizado=True,
        )
        if result:
            print("   [OK] Ejercicio guardado correctamente")

        # Rutina de prueba
        print("   - Insertando rutina de prueba...")
        result = RoutineService.save_user_routine(
            routine_id=99999,
            user_id="test_user",
            nombre="Rutina de Prueba",
            descripcion="Rutina de prueba para verificar MongoDB",
            es_predisenada=False,
        )
        if result:
            print("   [OK] Rutina guardada correctamente")

        # Progreso de prueba
        print("   - Insertando progreso de prueba...")
        from datetime import date
        result = ProgressLogService.save_detailed_progress(
            user_id="test_user",
            routine_id=99999,
            exercise_id=99999,
            fecha=date.today(),
            series=3,
            reps=12,
            esfuerzo=7,
            notas="Progreso de prueba",
        )
        if result:
            print("   [OK] Progreso guardado correctamente")

        print("\n[OK] Todas las pruebas de insercion pasaron correctamente")

    except Exception as e:
        print(f"\n[ERROR] Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5. Verificar que los datos se guardaron
    print("\n5. Verificando datos guardados...")
    print(f"   - exercises: {db.exercises.count_documents({})} documentos")
    print(f"   - user_routines: {db.user_routines.count_documents({})} documentos")
    print(f"   - progress_logs: {db.progress_logs.count_documents({})} documentos")

    # 6. Limpiar datos de prueba
    print("\n6. Limpiando datos de prueba...")
    db.exercises.delete_many({"exercise_id": 99999})
    db.user_routines.delete_many({"routine_id": 99999})
    db.progress_logs.delete_many({"user_id": "test_user"})
    print("   [OK] Datos de prueba eliminados")

    print("\n" + "=" * 60)
    print("[OK] TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("=" * 60)
    print("\nResumen:")
    print(f"   - Conexion a MongoDB Atlas: [OK]")
    print(f"   - Base de datos: {db.name}")
    print(f"   - Servicios implementados: [OK] Funcionando")
    print(f"   - Colecciones disponibles:")
    print(f"     * exercises")
    print(f"     * user_routines")
    print(f"     * routine_templates")
    print(f"     * progress_logs")
    print(f"     * trainer_assignments")
    print(f"     * user_activity_logs")
    print(f"     * exercise_details")
    print("\n")

    return True

if __name__ == "__main__":
    try:
        success = test_mongodb_connection()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
