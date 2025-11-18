#!/usr/bin/env python
"""
Script de verificación rápida del sistema Gym Icesi
Ejecutar: python verificar_sistema.py
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.contrib.auth.models import User
from fit.models import Exercise, Routine, ProgressLog, TrainerAssignment, TrainerRecommendation
from django.db import connection

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_warning(text):
    print(f"[WARNING] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def verificar_bd_institucional():
    """Verificar conexión y datos de la BD institucional"""
    print_header("VERIFICACIÓN DE BASE DE DATOS INSTITUCIONAL")
    
    try:
        with connection.cursor() as cur:
            # Verificar tabla users
            cur.execute("SELECT COUNT(*) FROM users WHERE is_active = true;")
            count = cur.fetchone()[0]
            print_success(f"Tabla 'users' accesible: {count} usuarios activos")
            
            # Verificar usuarios de prueba
            test_users = ['laura.h', 'paula.r', 'admin']
            for username in test_users:
                cur.execute("SELECT username, role FROM users WHERE username = %s;", [username])
                row = cur.fetchone()
                if row:
                    print_success(f"Usuario '{username}' existe (rol: {row[1]})")
                else:
                    print_error(f"Usuario '{username}' NO existe")
            
            # Verificar tabla employees
            cur.execute("SELECT COUNT(*) FROM employees WHERE UPPER(employee_type) = 'INSTRUCTOR';")
            count = cur.fetchone()[0]
            print_success(f"Entrenadores (Instructores): {count}")
            
    except Exception as e:
        print_error(f"Error al acceder a BD institucional: {e}")
        return False
    
    return True

def verificar_bd_aplicacion():
    """Verificar datos de la BD de la aplicación"""
    print_header("VERIFICACIÓN DE BASE DE DATOS DE LA APLICACIÓN")
    
    try:
        # Usuarios Django
        total_users = User.objects.count()
        print_success(f"Usuarios Django: {total_users}")
        
        # Ejercicios
        total_exercises = Exercise.objects.count()
        print_success(f"Ejercicios: {total_exercises}")
        
        # Rutinas
        total_routines = Routine.objects.count()
        print_success(f"Rutinas: {total_routines}")
        
        # Progresos
        total_progress = ProgressLog.objects.count()
        print_success(f"Registros de progreso: {total_progress}")
        
        # Asignaciones
        total_assignments = TrainerAssignment.objects.filter(activo=True).count()
        print_success(f"Asignaciones activas: {total_assignments}")
        
        # Recomendaciones
        total_recommendations = TrainerRecommendation.objects.count()
        print_success(f"Recomendaciones: {total_recommendations}")
        
    except Exception as e:
        print_error(f"Error al acceder a BD de aplicación: {e}")
        return False
    
    return True

def verificar_usuarios_roles():
    """Verificar que los usuarios tengan los roles correctos"""
    print_header("VERIFICACIÓN DE ROLES DE USUARIOS")
    
    try:
        # Usuario estándar
        user_std = User.objects.filter(username='laura.h').first()
        if user_std:
            if not user_std.is_staff and not user_std.is_superuser:
                print_success(f"Usuario estándar 'laura.h': OK (no staff, no superuser)")
            else:
                print_error(f"Usuario estándar 'laura.h': ERROR (tiene permisos incorrectos)")
        
        # Entrenador
        trainer = User.objects.filter(username='paula.r').first()
        if trainer:
            if trainer.is_staff and not trainer.is_superuser:
                print_success(f"Entrenador 'paula.r': OK (staff=True, superuser=False)")
            else:
                print_error(f"Entrenador 'paula.r': ERROR (permisos incorrectos)")
        
        # Administrador
        admin = User.objects.filter(username='admin').first()
        if admin:
            if admin.is_superuser:
                print_success(f"Administrador 'admin': OK (superuser=True)")
            else:
                print_error(f"Administrador 'admin': ERROR (no es superuser)")
        
    except Exception as e:
        print_error(f"Error al verificar roles: {e}")
        return False
    
    return True

def verificar_urls():
    """Verificar que las URLs principales estén configuradas"""
    print_header("VERIFICACIÓN DE URLs")
    
    from django.urls import reverse, NoReverseMatch
    
    urls_importantes = [
        ('index', []),
        ('home', []),
        ('exercises_list', []),
        ('routine_list', []),
        ('progress_list', []),
        ('report_progress', []),
        ('trainer_assignees', []),
        ('admin_assign_trainer', []),
    ]
    
    for url_name, args in urls_importantes:
        try:
            url = reverse(url_name, args=args)
            print_success(f"URL '{url_name}': {url}")
        except NoReverseMatch:
            print_error(f"URL '{url_name}': NO encontrada")
        except Exception as e:
            print_warning(f"URL '{url_name}': Error - {e}")

def verificar_modelos():
    """Verificar que los modelos estén correctamente definidos"""
    print_header("VERIFICACIÓN DE MODELOS")
    
    modelos = [
        ('Exercise', Exercise),
        ('Routine', Routine),
        ('ProgressLog', ProgressLog),
        ('TrainerAssignment', TrainerAssignment),
        ('TrainerRecommendation', TrainerRecommendation),
    ]
    
    for nombre, modelo in modelos:
        try:
            count = modelo.objects.count()
            print_success(f"Modelo '{nombre}': OK ({count} registros)")
        except Exception as e:
            print_error(f"Modelo '{nombre}': ERROR - {e}")

def main():
    print("\n" + "="*60)
    print("  VERIFICACIÓN DEL SISTEMA GYM ICESI")
    print("="*60)
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(("BD Institucional", verificar_bd_institucional()))
    resultados.append(("BD Aplicación", verificar_bd_aplicacion()))
    resultados.append(("Roles de Usuarios", verificar_usuarios_roles()))
    resultados.append(("Modelos", verificar_modelos()))
    verificar_urls()
    
    # Resumen
    print_header("RESUMEN")
    for nombre, resultado in resultados:
        if resultado:
            print_success(f"{nombre}: OK")
        else:
            print_error(f"{nombre}: ERROR")
    
    print("\n" + "="*60)
    print("  PRÓXIMOS PASOS")
    print("="*60)
    print_info("1. Abre http://127.0.0.1:8000/ en tu navegador")
    print_info("2. Prueba login con:")
    print_info("   - Usuario: laura.h / Contraseña: lh123")
    print_info("   - Entrenador: paula.r / Contraseña: pr123")
    print_info("   - Admin: admin / Contraseña: admin123")
    print_info("3. Sigue la guía: GUIA_PRUEBAS_COMPLETA.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

