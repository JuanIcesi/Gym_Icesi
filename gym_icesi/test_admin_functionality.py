"""
Script de prueba para verificar todas las funcionalidades del administrador
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.db import connection

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def verificar_usuario_admin():
    """Verificar si existe un usuario administrador"""
    print_header("VERIFICACIÓN DE USUARIO ADMINISTRADOR")
    
    # Buscar usuarios con role='ADMIN' en la BD institucional
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE role = 'ADMIN'")
            admins = cur.fetchall()
            
            if admins:
                print_success(f"Usuarios ADMIN encontrados en BD institucional: {[a[0] for a in admins]}")
                return admins[0][0]  # Retornar el primer admin
            else:
                print_info("No hay usuarios con role='ADMIN' en la BD institucional")
                print_info("Buscando usuarios que puedan ser administradores...")
                
                # Buscar usuarios con employee_type='ADMINISTRATIVO'
                cur.execute("""
                    SELECT u.username 
                    FROM users u
                    JOIN employees e ON u.employee_id = e.id
                    WHERE UPPER(e.employee_type) = 'ADMINISTRATIVO'
                """)
                admin_emps = cur.fetchall()
                
                if admin_emps:
                    print_success(f"Empleados ADMINISTRATIVO encontrados: {[a[0] for a in admin_emps]}")
                    print_info("NOTA: Estos usuarios necesitan tener role='ADMIN' para ser administradores")
                    return None
                else:
                    print_error("No se encontraron usuarios administradores")
                    print_info("Para crear un admin, ejecuta en Neon:")
                    print_info("UPDATE users SET role = 'ADMIN' WHERE username = 'maria.g';")
                    return None
    except Exception as e:
        print_error(f"Error al verificar usuario admin: {e}")
        return None

def probar_urls_admin(client, username, password):
    """Probar todas las URLs del administrador"""
    print_header("PRUEBA DE URLs DEL ADMINISTRADOR")
    
    # Login
    print_info(f"Iniciando sesión como {username}...")
    login_response = client.post('/login/', {
        'username': username,
        'password': password,
        'expected_role': 'admin'
    }, follow=True)
    
    if login_response.status_code != 200:
        print_error(f"Error en login: {login_response.status_code}")
        return False
    
    if not login_response.context or not login_response.context.get('user') or not login_response.context['user'].is_superuser:
        print_error("El usuario no tiene permisos de administrador")
        return False
    
    print_success("Login exitoso")
    
    # Lista de URLs a probar
    urls_to_test = [
        ('admin_dashboard', 'Dashboard de Administrador'),
        ('admin_users_management', 'Gestión de Usuarios'),
        ('admin_assign_trainer_advanced', 'Asignación Avanzada'),
        ('admin_assignment_history', 'Historial de Asignaciones'),
        ('admin_content_moderation', 'Moderación de Contenido'),
        ('admin_analytics', 'Analytics y Reportes'),
        ('admin_system_config', 'Configuración del Sistema'),
    ]
    
    resultados = []
    
    for url_name, descripcion in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            if response.status_code == 200:
                print_success(f"{descripcion}: OK (200)")
                resultados.append(True)
            elif response.status_code == 302:
                print_info(f"{descripcion}: Redirección (302) - posiblemente requiere autenticación")
                resultados.append(False)
            else:
                print_error(f"{descripcion}: Error {response.status_code}")
                resultados.append(False)
        except Exception as e:
            print_error(f"{descripcion}: Excepción - {e}")
            resultados.append(False)
    
    return all(resultados)

def probar_funcionalidades_admin(client):
    """Probar funcionalidades específicas del administrador"""
    print_header("PRUEBA DE FUNCIONALIDADES ESPECÍFICAS")
    
    # Probar gestión de usuarios
    print_info("Probando gestión de usuarios...")
    try:
        response = client.get(reverse('admin_users_management'))
        if response.status_code == 200:
            print_success("Gestión de usuarios: OK")
        else:
            print_error(f"Gestión de usuarios: Error {response.status_code}")
    except Exception as e:
        print_error(f"Gestión de usuarios: Excepción - {e}")
    
    # Probar asignación avanzada
    print_info("Probando asignación avanzada...")
    try:
        response = client.get(reverse('admin_assign_trainer_advanced'))
        if response.status_code == 200:
            print_success("Asignación avanzada: OK")
        else:
            print_error(f"Asignación avanzada: Error {response.status_code}")
    except Exception as e:
        print_error(f"Asignación avanzada: Excepción - {e}")
    
    # Probar analytics
    print_info("Probando analytics...")
    try:
        response = client.get(reverse('admin_analytics'))
        if response.status_code == 200:
            print_success("Analytics: OK")
        else:
            print_error(f"Analytics: Error {response.status_code}")
    except Exception as e:
        print_error(f"Analytics: Excepción - {e}")
    
    # Probar configuración del sistema
    print_info("Probando configuración del sistema...")
    try:
        response = client.get(reverse('admin_system_config'))
        if response.status_code == 200:
            print_success("Configuración del sistema: OK")
        else:
            print_error(f"Configuración del sistema: Error {response.status_code}")
    except Exception as e:
        print_error(f"Configuración del sistema: Excepción - {e}")

def main():
    print_header("PRUEBAS DE FUNCIONALIDADES DEL ADMINISTRADOR")
    
    # Verificar usuario admin
    admin_username = verificar_usuario_admin()
    
    if not admin_username:
        print_error("\n⚠️  No se encontró un usuario administrador para las pruebas")
        print_info("\nPara crear un administrador, ejecuta en Neon:")
        print_info("UPDATE users SET role = 'ADMIN' WHERE username = 'maria.g';")
        print_info("\nLuego reinicia el servidor y vuelve a ejecutar este script")
        return
    
    # Obtener contraseña (asumiendo formato hash_<password>)
    password = admin_username.split('.')[0] + '123' if '.' in admin_username else 'admin123'
    
    print_info(f"\nProbando con usuario: {admin_username}")
    print_info(f"Contraseña asumida: {password}")
    
    # Crear cliente de prueba
    client = Client()
    
    # Probar URLs
    urls_ok = probar_urls_admin(client, admin_username, password)
    
    # Probar funcionalidades
    probar_funcionalidades_admin(client)
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    if urls_ok:
        print_success("Todas las URLs del administrador funcionan correctamente")
    else:
        print_error("Algunas URLs del administrador tienen problemas")
    
    print_info("\nPruebas completadas")

if __name__ == '__main__':
    main()

