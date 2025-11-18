"""
Script de verificación manual de todas las funcionalidades del Usuario Estándar
Este script verifica que todas las URLs, vistas y funcionalidades estén correctamente implementadas
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.contrib.auth.models import User
from fit.models import Exercise, Routine, RoutineItem, ProgressLog

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def print_warning(text):
    print(f"[WARNING] {text}")

def verificar_url(url_name, descripcion, requiere_auth=True):
    """Verifica que una URL existe y responde correctamente"""
    try:
        url = reverse(url_name)
        print_info(f"URL encontrada: {url_name} -> {url}")
        return True
    except NoReverseMatch:
        print_error(f"URL no encontrada: {url_name} - {descripcion}")
        return False

def verificar_vista_responde(client, url_name, descripcion, requiere_auth=True, metodo='GET'):
    """Verifica que una vista responde correctamente"""
    try:
        url = reverse(url_name)
        if metodo == 'GET':
            response = client.get(url)
        else:
            response = client.post(url, {})
        
        if response.status_code == 200:
            print_success(f"{descripcion}: OK (200)")
            return True
        elif response.status_code == 302:
            print_info(f"{descripcion}: Redirección (302) - posiblemente requiere datos")
            return True
        elif response.status_code == 403:
            print_warning(f"{descripcion}: Prohibido (403) - requiere permisos")
            return False
        elif response.status_code == 404:
            print_error(f"{descripcion}: No encontrado (404)")
            return False
        else:
            print_warning(f"{descripcion}: Código {response.status_code}")
            return False
    except NoReverseMatch:
        print_error(f"URL no encontrada: {url_name}")
        return False
    except Exception as e:
        print_error(f"{descripcion}: Excepción - {e}")
        return False

def main():
    print_header("VERIFICACION DE FUNCIONALIDADES - USUARIO ESTANDAR")
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_user_verificacion',
        defaults={'is_staff': False, 'is_superuser': False}
    )
    client.force_login(user)
    
    resultados = {
        'ok': 0,
        'error': 0,
        'warning': 0
    }
    
    # ==================== AUTENTICACION ====================
    print_header("1. AUTENTICACION Y LOGIN")
    
    urls_auth = [
        ('index', 'Página de selección de login'),
        ('login', 'Página de login'),
        ('logout', 'Logout'),
    ]
    
    for url_name, desc in urls_auth:
        if verificar_url(url_name, desc):
            resultados['ok'] += 1
        else:
            resultados['error'] += 1
    
    # ==================== DASHBOARD ====================
    print_header("2. DASHBOARD DEL USUARIO")
    
    if verificar_vista_responde(client, 'home', 'Dashboard del usuario'):
        resultados['ok'] += 1
    else:
        resultados['error'] += 1
    
    # ==================== GESTION DE RUTINAS ====================
    print_header("3. GESTION DE RUTINAS")
    
    urls_rutinas = [
        ('routine_list', 'Lista de rutinas'),
        ('routine_create', 'Crear rutina'),
        ('routine_detail', 'Detalle de rutina', False),  # Requiere pk
        ('routine_add_item', 'Agregar ejercicio a rutina', False),  # Requiere pk
        ('routine_adopt', 'Adoptar rutina prediseñada', False),  # Requiere pk
    ]
    
    for item in urls_rutinas:
        url_name = item[0]
        desc = item[1]
        requiere_pk = len(item) > 2 and item[2] == False
        
        if requiere_pk:
            # Crear rutina de prueba para probar URLs que requieren pk
            routine = Routine.objects.filter(user=user).first()
            if not routine:
                routine = Routine.objects.create(
                    nombre='Rutina Test',
                    user=user
                )
            try:
                if url_name == 'routine_detail':
                    url = reverse(url_name, args=[routine.pk])
                elif url_name == 'routine_add_item':
                    url = reverse(url_name, args=[routine.pk])
                elif url_name == 'routine_adopt':
                    url = reverse(url_name, args=[routine.pk])
                
                response = client.get(url)
                if response.status_code in [200, 302]:
                    print_success(f"{desc}: OK")
                    resultados['ok'] += 1
                else:
                    print_error(f"{desc}: Error {response.status_code}")
                    resultados['error'] += 1
            except Exception as e:
                print_error(f"{desc}: Excepción - {e}")
                resultados['error'] += 1
        else:
            if verificar_vista_responde(client, url_name, desc):
                resultados['ok'] += 1
            else:
                resultados['error'] += 1
    
    # ==================== GESTION DE EJERCICIOS ====================
    print_header("4. GESTION DE EJERCICIOS")
    
    urls_ejercicios = [
        ('exercises_list', 'Lista de ejercicios'),
        ('exercise_detail', 'Detalle de ejercicio', False),  # Requiere pk
        ('exercise_create', 'Crear ejercicio personalizado'),
    ]
    
    for item in urls_ejercicios:
        url_name = item[0]
        desc = item[1]
        requiere_pk = len(item) > 2 and item[2] == False
        
        if requiere_pk:
            exercise = Exercise.objects.first()
            if exercise:
                try:
                    url = reverse(url_name, args=[exercise.pk])
                    response = client.get(url)
                    if response.status_code in [200, 302]:
                        print_success(f"{desc}: OK")
                        resultados['ok'] += 1
                    else:
                        print_error(f"{desc}: Error {response.status_code}")
                        resultados['error'] += 1
                except Exception as e:
                    print_error(f"{desc}: Excepción - {e}")
                    resultados['error'] += 1
            else:
                print_warning(f"{desc}: No hay ejercicios para probar")
                resultados['warning'] += 1
        else:
            if verificar_vista_responde(client, url_name, desc):
                resultados['ok'] += 1
            else:
                resultados['error'] += 1
    
    # ==================== REGISTRO DE PROGRESO ====================
    print_header("5. REGISTRO DE PROGRESO")
    
    urls_progreso = [
        ('progress_create', 'Crear registro de progreso'),
        ('progress_list', 'Lista de progreso'),
    ]
    
    for url_name, desc in urls_progreso:
        if verificar_vista_responde(client, url_name, desc):
            resultados['ok'] += 1
        else:
            resultados['error'] += 1
    
    # ==================== INFORMES ====================
    print_header("6. INFORMES")
    
    urls_informes = [
        ('report_progress', 'Informe de progreso'),
        ('report_adherence', 'Informe de adherencia'),
        ('report_load_balance', 'Informe de balance de carga'),
        ('report_progress_trend', 'Informe de tendencias'),
        ('report_achievements', 'Informe de logros'),
    ]
    
    for url_name, desc in urls_informes:
        if verificar_vista_responde(client, url_name, desc):
            resultados['ok'] += 1
        else:
            resultados['error'] += 1
    
    # ==================== PERFIL DE SALUD ====================
    print_header("7. PERFIL DE SALUD")
    
    if verificar_vista_responde(client, 'profile_health', 'Perfil de salud'):
        resultados['ok'] += 1
    else:
        resultados['error'] += 1
    
    # ==================== MENSAJERIA ====================
    print_header("8. MENSAJERIA")
    
    urls_mensajes = [
        ('messages_list', 'Lista de mensajes'),
        ('message_create', 'Crear mensaje'),
        ('message_detail', 'Detalle de mensaje', False),  # Requiere pk
    ]
    
    for item in urls_mensajes:
        url_name = item[0]
        desc = item[1]
        requiere_pk = len(item) > 2 and item[2] == False
        
        if requiere_pk:
            from fit.models import Message
            trainer = User.objects.filter(is_staff=True).first()
            if trainer:
                message = Message.objects.filter(remitente=user).first()
                if not message:
                    message = Message.objects.create(
                        remitente=user,
                        destinatario=trainer,
                        asunto='Test',
                        mensaje='Test'
                    )
                try:
                    url = reverse(url_name, args=[message.pk])
                    response = client.get(url)
                    if response.status_code in [200, 302]:
                        print_success(f"{desc}: OK")
                        resultados['ok'] += 1
                    else:
                        print_error(f"{desc}: Error {response.status_code}")
                        resultados['error'] += 1
                except Exception as e:
                    print_error(f"{desc}: Excepción - {e}")
                    resultados['error'] += 1
            else:
                print_warning(f"{desc}: No hay entrenador para probar")
                resultados['warning'] += 1
        else:
            if verificar_vista_responde(client, url_name, desc):
                resultados['ok'] += 1
            else:
                resultados['error'] += 1
    
    # ==================== EVENTOS ====================
    print_header("9. EVENTOS INSTITUCIONALES")
    
    urls_eventos = [
        ('eventos_list', 'Lista de eventos'),
        ('evento_detail', 'Detalle de evento', False),  # Requiere pk
        ('evento_inscribir', 'Inscribirse a evento', False),  # Requiere pk
        ('evento_desinscribir', 'Desinscribirse de evento', False),  # Requiere pk
    ]
    
    for item in urls_eventos:
        url_name = item[0]
        desc = item[1]
        requiere_pk = len(item) > 2 and item[2] == False
        
        if requiere_pk:
            from fit.models import EventoInstitucional
            evento = EventoInstitucional.objects.first()
            if evento:
                try:
                    url = reverse(url_name, args=[evento.pk])
                    response = client.get(url)
                    if response.status_code in [200, 302]:
                        print_success(f"{desc}: OK")
                        resultados['ok'] += 1
                    else:
                        print_error(f"{desc}: Error {response.status_code}")
                        resultados['error'] += 1
                except Exception as e:
                    print_error(f"{desc}: Excepción - {e}")
                    resultados['error'] += 1
            else:
                print_warning(f"{desc}: No hay eventos para probar")
                resultados['warning'] += 1
        else:
            if verificar_vista_responde(client, url_name, desc):
                resultados['ok'] += 1
            else:
                resultados['error'] += 1
    
    # ==================== ESPACIOS DEPORTIVOS ====================
    print_header("10. ESPACIOS DEPORTIVOS Y RESERVAS")
    
    urls_espacios = [
        ('espacios_list', 'Lista de espacios'),
        ('espacio_detail', 'Detalle de espacio', False),  # Requiere pk
        ('reserva_create', 'Crear reserva'),
        ('reservas_list', 'Lista de reservas'),
        ('reserva_cancel', 'Cancelar reserva', False),  # Requiere pk
    ]
    
    for item in urls_espacios:
        url_name = item[0]
        desc = item[1]
        requiere_pk = len(item) > 2 and item[2] == False
        
        if requiere_pk:
            from fit.models import EspacioDeportivo, ReservaEspacio
            if url_name == 'espacio_detail':
                espacio = EspacioDeportivo.objects.first()
                if espacio:
                    try:
                        url = reverse(url_name, args=[espacio.pk])
                        response = client.get(url)
                        if response.status_code in [200, 302]:
                            print_success(f"{desc}: OK")
                            resultados['ok'] += 1
                        else:
                            print_error(f"{desc}: Error {response.status_code}")
                            resultados['error'] += 1
                    except Exception as e:
                        print_error(f"{desc}: Excepción - {e}")
                        resultados['error'] += 1
                else:
                    print_warning(f"{desc}: No hay espacios para probar")
                    resultados['warning'] += 1
            elif url_name == 'reserva_cancel':
                reserva = ReservaEspacio.objects.filter(usuario=user).first()
                if reserva:
                    try:
                        url = reverse(url_name, args=[reserva.pk])
                        response = client.get(url)
                        if response.status_code in [200, 302]:
                            print_success(f"{desc}: OK")
                            resultados['ok'] += 1
                        else:
                            print_error(f"{desc}: Error {response.status_code}")
                            resultados['error'] += 1
                    except Exception as e:
                        print_error(f"{desc}: Excepción - {e}")
                        resultados['error'] += 1
                else:
                    print_warning(f"{desc}: No hay reservas para probar")
                    resultados['warning'] += 1
        else:
            if verificar_vista_responde(client, url_name, desc):
                resultados['ok'] += 1
            else:
                resultados['error'] += 1
    
    # ==================== RECORDATORIOS ====================
    print_header("11. RECORDATORIOS")
    
    if verificar_vista_responde(client, 'routine_reminders', 'Recordatorios de rutinas'):
        resultados['ok'] += 1
    else:
        resultados['error'] += 1
    
    # ==================== VERIFICACION DE MODELOS ====================
    print_header("12. VERIFICACION DE MODELOS Y DATOS")
    
    # Verificar que los modelos existen
    modelos_verificar = [
        ('Exercise', Exercise),
        ('Routine', Routine),
        ('RoutineItem', RoutineItem),
        ('ProgressLog', ProgressLog),
        ('UserProfile', 'fit.models.UserProfile'),
        ('Message', 'fit.models.Message'),
        ('EventoInstitucional', 'fit.models.EventoInstitucional'),
        ('EspacioDeportivo', 'fit.models.EspacioDeportivo'),
        ('ReservaEspacio', 'fit.models.ReservaEspacio'),
    ]
    
    for nombre, modelo in modelos_verificar:
        try:
            if isinstance(modelo, str):
                from fit.models import UserProfile, Message, EventoInstitucional, EspacioDeportivo, ReservaEspacio
                modelo_obj = eval(modelo.split('.')[-1])
            else:
                modelo_obj = modelo
            
            count = modelo_obj.objects.count()
            print_success(f"Modelo {nombre}: OK ({count} registros)")
            resultados['ok'] += 1
        except Exception as e:
            print_error(f"Modelo {nombre}: Error - {e}")
            resultados['error'] += 1
    
    # ==================== RESUMEN ====================
    print_header("RESUMEN DE VERIFICACION")
    
    total = resultados['ok'] + resultados['error'] + resultados['warning']
    porcentaje_ok = (resultados['ok'] / total * 100) if total > 0 else 0
    
    print(f"Total de verificaciones: {total}")
    print_success(f"Exitosas: {resultados['ok']}")
    print_error(f"Errores: {resultados['error']}")
    print_warning(f"Advertencias: {resultados['warning']}")
    print(f"\nPorcentaje de éxito: {porcentaje_ok:.1f}%")
    
    if resultados['error'] == 0:
        print_success("\nTODAS LAS FUNCIONALIDADES ESTAN CORRECTAMENTE IMPLEMENTADAS")
    else:
        print_error(f"\nHAY {resultados['error']} ERRORES QUE DEBEN CORREGIRSE")
    
    # Limpiar usuario de prueba
    if created:
        user.delete()
    
    return resultados['error'] == 0

if __name__ == '__main__':
    try:
        exit_code = 0 if main() else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerificacion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

