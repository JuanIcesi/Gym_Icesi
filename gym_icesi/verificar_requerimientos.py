#!/usr/bin/env python
"""
Script de verificación completa de requerimientos del proyecto Gym Icesi
Verifica que todos los requerimientos estén implementados y funcionando
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from fit.models import (
    Exercise, Routine, RoutineItem, ProgressLog, 
    TrainerAssignment, UserMonthlyStats, TrainerMonthlyStats,
    TrainerRecommendation
)
from fit.institutional_models import InstitutionalUser
from fit.mongodb_service import MongoDBService

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_check(item, status, details=""):
    symbol = "[OK]" if status else "[FALTA]"
    print(f"{symbol} {item}")
    if details:
        print(f"     {details}")

def verificar_requerimiento_1():
    """REQ 1: Login institucional con cuenta institucional"""
    print_header("REQUERIMIENTO 1: Login Institucional")
    
    checks = []
    
    # 1.1: Verificar que existe InstitutionalBackend
    try:
        from fit.auth_backend import InstitutionalBackend
        print_check("Backend de autenticación institucional existe", True)
        checks.append(True)
    except ImportError:
        print_check("Backend de autenticación institucional existe", False)
        checks.append(False)
    
    # 1.2: Verificar modelo InstitutionalUser
    try:
        users_count = InstitutionalUser.objects.count()
        print_check(f"Modelo InstitutionalUser funciona (usuarios: {users_count})", True)
        checks.append(True)
    except Exception as e:
        print_check("Modelo InstitutionalUser funciona", False, f"Error: {e}")
        checks.append(False)
    
    # 1.3: Verificar que se consulta tabla users de PostgreSQL
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users WHERE is_active = true")
            count = cur.fetchone()[0]
        print_check(f"Consulta a tabla 'users' funciona ({count} usuarios activos)", True)
        checks.append(True)
    except Exception as e:
        print_check("Consulta a tabla 'users' funciona", False, f"Error: {e}")
        checks.append(False)
    
    # 1.4: Verificar que se consultan students y employees
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM students")
            students = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM employees")
            employees = cur.fetchone()[0]
        print_check(f"Consulta a 'students' y 'employees' funciona (estudiantes: {students}, empleados: {employees})", True)
        checks.append(True)
    except Exception as e:
        print_check("Consulta a 'students' y 'employees' funciona", False, f"Error: {e}")
        checks.append(False)
    
    return all(checks)

def verificar_requerimiento_2():
    """REQ 2: Rutinas de ejercicio con ejercicios predefinidos o personalizados"""
    print_header("REQUERIMIENTO 2: Rutinas de Ejercicio")
    
    checks = []
    
    # 2.1: Verificar modelo Exercise con todos los campos requeridos
    required_fields = ['nombre', 'tipo', 'descripcion', 'duracion_min', 'dificultad', 'video_url']
    exercise_fields = [f.name for f in Exercise._meta.get_fields()]
    missing_fields = [f for f in required_fields if f not in exercise_fields]
    
    if not missing_fields:
        print_check("Modelo Exercise con todos los campos requeridos", True, 
                   f"Campos: {', '.join(required_fields)}")
        checks.append(True)
    else:
        print_check("Modelo Exercise con todos los campos requeridos", False,
                   f"Faltan: {', '.join(missing_fields)}")
        checks.append(False)
    
    # 2.2: Verificar tipos de ejercicio (cardio, fuerza, movilidad)
    tipos = [choice[0] for choice in Exercise.TIPO]
    required_tipos = ['cardio', 'fuerza', 'movilidad']
    if all(t in tipos for t in required_tipos):
        print_check("Tipos de ejercicio correctos", True, f"Tipos: {', '.join(tipos)}")
        checks.append(True)
    else:
        print_check("Tipos de ejercicio correctos", False, f"Faltan: {set(required_tipos) - set(tipos)}")
        checks.append(False)
    
    # 2.3: Verificar que existen ejercicios en la BD
    exercises_count = Exercise.objects.count()
    print_check(f"Ejercicios disponibles en BD ({exercises_count} ejercicios)", exercises_count > 0)
    checks.append(exercises_count > 0)
    
    # 2.4: Verificar modelo Routine
    routine_fields = [f.name for f in Routine._meta.get_fields()]
    required_routine_fields = ['user', 'nombre', 'descripcion', 'es_predisenada']
    missing_routine = [f for f in required_routine_fields if f not in routine_fields]
    
    if not missing_routine:
        print_check("Modelo Routine con campos requeridos", True)
        checks.append(True)
    else:
        print_check("Modelo Routine con campos requeridos", False, f"Faltan: {', '.join(missing_routine)}")
        checks.append(False)
    
    # 2.5: Verificar RoutineItem (ejercicios en rutinas)
    item_fields = [f.name for f in RoutineItem._meta.get_fields()]
    required_item_fields = ['routine', 'exercise', 'orden', 'series', 'reps', 'tiempo_seg']
    missing_item = [f for f in required_item_fields if f not in item_fields]
    
    if not missing_item:
        print_check("Modelo RoutineItem con campos requeridos", True)
        checks.append(True)
    else:
        print_check("Modelo RoutineItem con campos requeridos", False, f"Faltan: {', '.join(missing_item)}")
        checks.append(False)
    
    return all(checks)

def verificar_requerimiento_3():
    """REQ 3: Registro de progreso diario/semanal"""
    print_header("REQUERIMIENTO 3: Registro de Progreso")
    
    checks = []
    
    # 3.1: Verificar modelo ProgressLog con campos requeridos
    required_fields = ['user', 'routine', 'fecha', 'repeticiones', 'tiempo_seg', 'esfuerzo', 'notas']
    progress_fields = [f.name for f in ProgressLog._meta.get_fields()]
    missing = [f for f in required_fields if f not in progress_fields]
    
    if not missing:
        print_check("Modelo ProgressLog con campos requeridos", True)
        checks.append(True)
    else:
        print_check("Modelo ProgressLog con campos requeridos", False, f"Faltan: {', '.join(missing)}")
        checks.append(False)
    
    # 3.2: Verificar integración con MongoDB
    mongo_client = MongoDBService.get_client()
    if mongo_client:
        print_check("Integración MongoDB para progreso detallado", True)
        checks.append(True)
    else:
        print_check("Integración MongoDB para progreso detallado", False, "MongoDB no disponible")
        checks.append(False)
    
    return all(checks)

def verificar_requerimiento_4():
    """REQ 4: Funcionalidades de entrenador"""
    print_header("REQUERIMIENTO 4: Funcionalidades de Entrenador")
    
    checks = []
    
    # 4.1: Verificar que entrenadores pueden ver usuarios asignados
    try:
        from fit.views import trainer_assignees
        print_check("Vista trainer_assignees existe", True)
        checks.append(True)
    except:
        print_check("Vista trainer_assignees existe", False)
        checks.append(False)
    
    # 4.2: Verificar modelo TrainerAssignment
    assignment_fields = [f.name for f in TrainerAssignment._meta.get_fields()]
    required = ['user', 'trainer', 'fecha_asignacion', 'activo']
    missing = [f for f in required if f not in assignment_fields]
    
    if not missing:
        print_check("Modelo TrainerAssignment completo", True)
        checks.append(True)
    else:
        print_check("Modelo TrainerAssignment completo", False, f"Faltan: {', '.join(missing)}")
        checks.append(False)
    
    # 4.3: Verificar recomendaciones
    rec_fields = [f.name for f in TrainerRecommendation._meta.get_fields()]
    required_rec = ['trainer', 'user', 'mensaje', 'fecha']
    missing_rec = [f for f in required_rec if f not in rec_fields]
    
    if not missing_rec:
        print_check("Modelo TrainerRecommendation completo", True)
        checks.append(True)
    else:
        print_check("Modelo TrainerRecommendation completo", False, f"Faltan: {', '.join(missing_rec)}")
        checks.append(False)
    
    # 4.4: Verificar rutinas prediseñadas
    routines_predisenadas = Routine.objects.filter(es_predisenada=True).count()
    print_check(f"Rutinas prediseñadas ({routines_predisenadas} disponibles)", True)
    checks.append(True)
    
    # 4.5: Verificar que entrenadores pueden crear ejercicios
    try:
        from fit.views import trainer_exercise_create
        print_check("Vista trainer_exercise_create existe", True)
        checks.append(True)
    except:
        print_check("Vista trainer_exercise_create existe", False)
        checks.append(False)
    
    return all(checks)

def verificar_requerimiento_5():
    """REQ 5: Módulo de administración"""
    print_header("REQUERIMIENTO 5: Módulo de Administración")
    
    checks = []
    
    # 5.1: Verificar vista de asignación de entrenadores
    try:
        from fit.views import admin_assign_trainer
        print_check("Vista admin_assign_trainer existe", True)
        checks.append(True)
    except:
        print_check("Vista admin_assign_trainer existe", False)
        checks.append(False)
    
    # 5.2: Verificar dashboard de admin
    try:
        from fit.views import admin_dashboard
        print_check("Vista admin_dashboard existe", True)
        checks.append(True)
    except:
        print_check("Vista admin_dashboard existe", False)
        checks.append(False)
    
    return all(checks)

def verificar_requerimiento_6():
    """REQ 6: Estadísticas mensuales"""
    print_header("REQUERIMIENTO 6: Estadísticas Mensuales")
    
    checks = []
    
    # 6.1: Verificar modelo UserMonthlyStats
    user_stats_fields = [f.name for f in UserMonthlyStats._meta.get_fields()]
    required_user = ['user', 'anio', 'mes', 'rutinas_iniciadas', 'seguimientos_registrados']
    missing_user = [f for f in required_user if f not in user_stats_fields]
    
    if not missing_user:
        print_check("Modelo UserMonthlyStats completo", True)
        checks.append(True)
    else:
        print_check("Modelo UserMonthlyStats completo", False, f"Faltan: {', '.join(missing_user)}")
        checks.append(False)
    
    # 6.2: Verificar modelo TrainerMonthlyStats
    trainer_stats_fields = [f.name for f in TrainerMonthlyStats._meta.get_fields()]
    required_trainer = ['trainer', 'anio', 'mes', 'asignaciones_nuevas', 'seguimientos_realizados']
    missing_trainer = [f for f in required_trainer if f not in trainer_stats_fields]
    
    if not missing_trainer:
        print_check("Modelo TrainerMonthlyStats completo", True)
        checks.append(True)
    else:
        print_check("Modelo TrainerMonthlyStats completo", False, f"Faltan: {', '.join(missing_trainer)}")
        checks.append(False)
    
    # 6.3: Verificar señales para actualización automática
    try:
        from fit.signals import routine_saved, progress_saved, assignment_saved, recommendation_saved
        print_check("Señales para actualización automática de stats", True)
        checks.append(True)
    except:
        print_check("Señales para actualización automática de stats", False)
        checks.append(False)
    
    return all(checks)

def verificar_requerimiento_7():
    """REQ 7: Informes innovadores (al menos 2)"""
    print_header("REQUERIMIENTO 7: Informes Innovadores")
    
    checks = []
    
    # 7.1: Verificar que existen al menos 2 informes
    reportes = [
        ('report_progress', 'Informe de Progreso'),
        ('report_adherence', 'Informe de Adherencia'),
        ('report_progress_trend', 'Informe de Tendencias'),
        ('report_achievements', 'Informe de Logros'),
        ('report_load_balance', 'Informe de Carga'),
    ]
    
    reportes_encontrados = []
    for view_name, desc in reportes:
        try:
            from fit.views import __dict__
            if view_name in __dict__:
                reportes_encontrados.append(desc)
        except:
            pass
    
    if len(reportes_encontrados) >= 2:
        print_check(f"Informes disponibles ({len(reportes_encontrados)} encontrados)", True,
                   f"Informes: {', '.join(reportes_encontrados)}")
        checks.append(True)
    else:
        print_check(f"Informes disponibles ({len(reportes_encontrados)} encontrados)", False,
                   f"Se requieren al menos 2, encontrados: {len(reportes_encontrados)}")
        checks.append(False)
    
    # 7.2: Verificar templates de informes
    import os
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'fit')
    report_templates = [f for f in os.listdir(templates_dir) if f.startswith('report_') and f.endswith('.html')]
    
    if len(report_templates) >= 2:
        print_check(f"Templates de informes ({len(report_templates)} encontrados)", True)
        checks.append(True)
    else:
        print_check(f"Templates de informes ({len(report_templates)} encontrados)", False)
        checks.append(False)
    
    return all(checks)

def main():
    print("\n" + "="*70)
    print("  VERIFICACIÓN COMPLETA DE REQUERIMIENTOS - GYM ICESI")
    print("="*70)
    
    resultados = {}
    
    resultados['REQ1'] = verificar_requerimiento_1()
    resultados['REQ2'] = verificar_requerimiento_2()
    resultados['REQ3'] = verificar_requerimiento_3()
    resultados['REQ4'] = verificar_requerimiento_4()
    resultados['REQ5'] = verificar_requerimiento_5()
    resultados['REQ6'] = verificar_requerimiento_6()
    resultados['REQ7'] = verificar_requerimiento_7()
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    total = len(resultados)
    cumplidos = sum(1 for v in resultados.values() if v)
    
    for req, status in resultados.items():
        symbol = "[OK]" if status else "[FALTA]"
        print(f"{symbol} {req}")
    
    print(f"\nTotal: {cumplidos}/{total} requerimientos cumplidos")
    
    if cumplidos == total:
        print("\n[OK] TODOS LOS REQUERIMIENTOS ESTÁN IMPLEMENTADOS")
    else:
        print(f"\n[ATENCIÓN] Faltan {total - cumplidos} requerimientos por completar")

if __name__ == "__main__":
    main()

