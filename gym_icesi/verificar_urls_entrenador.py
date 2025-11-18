"""
Script simple para verificar que todas las URLs del entrenador están configuradas
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def verificar_url(url_name, descripcion, requiere_pk=False, requiere_user_id=False):
    """Verifica que una URL existe"""
    try:
        if requiere_pk:
            url = reverse(url_name, args=[1])
            print_success(f"{descripcion}: {url_name} -> {url} (requiere pk)")
        elif requiere_user_id:
            url = reverse(url_name, args=[1])
            print_success(f"{descripcion}: {url_name} -> {url} (requiere user_id)")
        else:
            url = reverse(url_name)
            print_success(f"{descripcion}: {url_name} -> {url}")
        return True
    except NoReverseMatch:
        print_error(f"{descripcion}: URL '{url_name}' NO ENCONTRADA")
        return False
    except Exception as e:
        print_error(f"{descripcion}: Error - {e}")
        return False

def main():
    print_header("VERIFICACION DE URLs - ENTRENADOR")
    
    resultados = {'ok': 0, 'error': 0}
    
    # URLs a verificar
    urls = [
        # Autenticación
        ('index', 'Página de selección de login', False, False),
        ('login', 'Página de login', False, False),
        ('logout', 'Logout', False, False),
        ('home', 'Dashboard del entrenador', False, False),
        
        # Gestión de usuarios asignados
        ('trainer_assignees', 'Lista de usuarios asignados', False, False),
        ('trainer_feedback', 'Detalle de usuario asignado', False, True),
        
        # Seguimiento de progreso
        ('trainer_progress_analysis', 'Análisis de progreso de usuario', False, True),
        
        # Sistema de recomendaciones
        ('trainer_recommendation_create', 'Crear recomendación simple', False, True),
        ('trainer_recommendation_advanced', 'Crear recomendación avanzada', False, True),
        
        # Creación de contenido
        ('trainer_routines', 'Lista de rutinas prediseñadas', False, False),
        ('trainer_routine_create', 'Crear rutina prediseñada', False, False),
        ('trainer_exercises', 'Lista de ejercicios del entrenador', False, False),
        ('trainer_exercise_create', 'Crear ejercicio', False, False),
        
        # Mensajería (también disponible para entrenadores)
        ('messages_list', 'Lista de mensajes', False, False),
        ('message_create', 'Crear mensaje', False, False),
        ('message_detail', 'Detalle de mensaje', True, False),
    ]
    
    for item in urls:
        url_name = item[0]
        desc = item[1]
        requiere_pk = item[2] if len(item) > 2 else False
        requiere_user_id = item[3] if len(item) > 3 else False
        
        if verificar_url(url_name, desc, requiere_pk, requiere_user_id):
            resultados['ok'] += 1
        else:
            resultados['error'] += 1
    
    # Resumen
    print_header("RESUMEN")
    total = resultados['ok'] + resultados['error']
    porcentaje = (resultados['ok'] / total * 100) if total > 0 else 0
    
    print(f"Total de URLs verificadas: {total}")
    print_success(f"URLs encontradas: {resultados['ok']}")
    print_error(f"URLs no encontradas: {resultados['error']}")
    print(f"Porcentaje de éxito: {porcentaje:.1f}%")
    
    if resultados['error'] == 0:
        print_success("\nTODAS LAS URLs ESTAN CORRECTAMENTE CONFIGURADAS")
        return True
    else:
        print_error(f"\nHAY {resultados['error']} URLs QUE NO ESTAN CONFIGURADAS")
        return False

if __name__ == '__main__':
    try:
        exit_code = 0 if main() else 1
        sys.exit(exit_code)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

