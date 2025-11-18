"""
Script simple para verificar que todas las URLs del usuario estándar están configuradas
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

def verificar_url(url_name, descripcion, requiere_pk=False):
    """Verifica que una URL existe"""
    try:
        if requiere_pk:
            # Para URLs que requieren pk, usar un pk dummy
            url = reverse(url_name, args=[1])
            print_success(f"{descripcion}: {url_name} -> {url} (requiere pk)")
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
    print_header("VERIFICACION DE URLs - USUARIO ESTANDAR")
    
    resultados = {'ok': 0, 'error': 0}
    
    # URLs a verificar
    urls = [
        # Autenticación
        ('index', 'Página de selección de login'),
        ('login', 'Página de login'),
        ('logout', 'Logout'),
        ('home', 'Dashboard del usuario'),
        
        # Rutinas
        ('routine_list', 'Lista de rutinas', False),
        ('routine_create', 'Crear rutina', False),
        ('routine_detail', 'Detalle de rutina', True),
        ('routine_add_item', 'Agregar ejercicio a rutina', True),
        ('routine_adopt', 'Adoptar rutina prediseñada', True),
        
        # Ejercicios
        ('exercises_list', 'Lista de ejercicios', False),
        ('exercise_detail', 'Detalle de ejercicio', True),
        ('exercise_create', 'Crear ejercicio personalizado', False),
        
        # Progreso
        ('progress_create', 'Crear registro de progreso', False),
        ('progress_list', 'Lista de progreso', False),
        
        # Informes
        ('report_progress', 'Informe de progreso', False),
        ('report_adherence', 'Informe de adherencia', False),
        ('report_load_balance', 'Informe de balance de carga', False),
        ('report_progress_trend', 'Informe de tendencias', False),
        ('report_achievements', 'Informe de logros', False),
        
        # Perfil de salud
        ('profile_health', 'Perfil de salud', False),
        
        # Mensajería
        ('messages_list', 'Lista de mensajes', False),
        ('message_create', 'Crear mensaje', False),
        ('message_detail', 'Detalle de mensaje', True),
        
        # Eventos
        ('eventos_list', 'Lista de eventos', False),
        ('evento_detail', 'Detalle de evento', True),
        ('evento_inscribir', 'Inscribirse a evento', True),
        ('evento_desinscribir', 'Desinscribirse de evento', True),
        
        # Espacios y reservas
        ('espacios_list', 'Lista de espacios', False),
        ('espacio_detail', 'Detalle de espacio', True),
        ('reserva_create', 'Crear reserva', False),
        ('reservas_list', 'Lista de reservas', False),
        ('reserva_cancel', 'Cancelar reserva', True),
        
        # Recordatorios
        ('routine_reminders', 'Recordatorios de rutinas', False),
    ]
    
    for item in urls:
        url_name = item[0]
        desc = item[1]
        requiere_pk = item[2] if len(item) > 2 else False
        
        if verificar_url(url_name, desc, requiere_pk):
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

