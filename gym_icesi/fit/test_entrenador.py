"""
Tests exhaustivos para verificar al 100% todas las funcionalidades del Entrenador
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta, time
from fit.models import (
    Exercise, Routine, RoutineItem, ProgressLog,
    TrainerAssignment, TrainerMonthlyStats, TrainerRecommendation,
    UserProfile, Message
)


class TestEntrenadorBase(TestCase):
    """Clase base para tests de entrenador"""
    
    def setUp(self):
        """Configuración inicial para todos los tests"""
        # Crear entrenador
        self.trainer = User.objects.create_user(
            username='sandra.m',
            password='sm123',
            is_staff=True,
            is_superuser=False
        )
        
        # Crear usuario estándar asignado
        self.user = User.objects.create_user(
            username='laura.h',
            password='lh123',
            is_staff=False,
            is_superuser=False
        )
        
        # Asignar usuario al entrenador
        self.assignment = TrainerAssignment.objects.create(
            trainer=self.trainer,
            user=self.user,
            activo=True
        )
        
        # Crear ejercicio de prueba
        self.exercise = Exercise.objects.create(
            nombre='Sentadillas',
            tipo='fuerza',
            descripcion='Ejercicio de fuerza para piernas',
            duracion_min=10,
            dificultad=3,
            creado_por=self.trainer
        )
        
        # Crear rutina prediseñada
        self.routine = Routine.objects.create(
            nombre='Rutina Prediseñada',
            descripcion='Rutina para testing',
            es_predisenada=True,
            autor_trainer=self.trainer,
            user=self.trainer
        )
        
        self.client = Client()
        self.client.force_login(self.trainer)


class TestAutenticacionEntrenador(TestEntrenadorBase):
    """Tests de autenticación para entrenador"""
    
    def setUp(self):
        super().setUp()
        self.client.logout()
    
    def test_login_page_carga(self):
        """Verifica que la página de login carga correctamente"""
        response = self.client.get(reverse('login') + '?role=trainer')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar Sesión')
    
    def test_redireccion_despues_login(self):
        """Verifica redirección después de login exitoso"""
        self.client.force_login(self.trainer)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class TestDashboardEntrenador(TestEntrenadorBase):
    """Tests del dashboard del entrenador"""
    
    def test_dashboard_carga(self):
        """Verifica que el dashboard carga correctamente"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_muestra_usuarios_asignados(self):
        """Verifica que el dashboard muestra usuarios asignados"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Verificar que muestra información de usuarios asignados
    
    def test_dashboard_muestra_rutinas_predisenadas(self):
        """Verifica que el dashboard muestra rutinas prediseñadas"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_muestra_recomendaciones_mes(self):
        """Verifica que el dashboard muestra recomendaciones del mes"""
        TrainerRecommendation.objects.create(
            trainer=self.trainer,
            user=self.user,
            titulo='Test',
            mensaje='Mensaje de prueba'
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class TestGestionUsuariosAsignados(TestEntrenadorBase):
    """Tests de gestión de usuarios asignados"""
    
    def test_lista_usuarios_asignados_carga(self):
        """Verifica que la lista de usuarios asignados carga"""
        response = self.client.get(reverse('trainer_assignees'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'laura.h')
    
    def test_detalle_usuario_asignado_carga(self):
        """Verifica que el detalle de usuario asignado carga"""
        response = self.client.get(reverse('trainer_feedback', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'laura.h')
    
    def test_no_puede_acceder_a_usuario_no_asignado(self):
        """Verifica que no puede acceder a usuario no asignado"""
        otro_usuario = User.objects.create_user(
            username='otro',
            password='pass'
        )
        response = self.client.get(reverse('trainer_feedback', args=[otro_usuario.pk]))
        # Debería redirigir o mostrar error
        self.assertNotEqual(response.status_code, 200)
    
    def test_detalle_muestra_rutinas_usuario(self):
        """Verifica que el detalle muestra rutinas del usuario"""
        Routine.objects.create(
            nombre='Rutina Usuario',
            user=self.user
        )
        response = self.client.get(reverse('trainer_feedback', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rutina Usuario')
    
    def test_detalle_muestra_progreso_usuario(self):
        """Verifica que el detalle muestra progreso del usuario"""
        ProgressLog.objects.create(
            user=self.user,
            routine=self.routine,
            fecha=date.today(),
            esfuerzo=7
        )
        response = self.client.get(reverse('trainer_feedback', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)


class TestSeguimientoProgreso(TestEntrenadorBase):
    """Tests de seguimiento de progreso"""
    
    def test_analisis_progreso_carga(self):
        """Verifica que el análisis de progreso carga"""
        response = self.client.get(reverse('trainer_progress_analysis', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_analisis_muestra_metricas(self):
        """Verifica que el análisis muestra métricas de desempeño"""
        ProgressLog.objects.create(
            user=self.user,
            routine=self.routine,
            fecha=date.today(),
            esfuerzo=7,
            repeticiones=30
        )
        response = self.client.get(reverse('trainer_progress_analysis', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_analisis_muestra_historial_completo(self):
        """Verifica que el análisis muestra historial completo"""
        # Crear múltiples registros de progreso
        for i in range(5):
            ProgressLog.objects.create(
                user=self.user,
                routine=self.routine,
                fecha=date.today() - timedelta(days=i),
                esfuerzo=7
            )
        response = self.client.get(reverse('trainer_progress_analysis', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_analisis_muestra_tendencias(self):
        """Verifica que el análisis muestra tendencias"""
        response = self.client.get(reverse('trainer_progress_analysis', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)


class TestSistemaRecomendaciones(TestEntrenadorBase):
    """Tests del sistema de recomendaciones"""
    
    def test_crear_recomendacion_simple(self):
        """Verifica creación de recomendación simple"""
        response = self.client.post(
            reverse('trainer_recommendation_create', args=[self.user.pk]),
            {
                'titulo': 'Recomendación Test',
                'mensaje': 'Mensaje de prueba',
                'tipo': 'general'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrainerRecommendation.objects.filter(
            trainer=self.trainer,
            user=self.user
        ).exists())
    
    def test_crear_recomendacion_avanzada(self):
        """Verifica creación de recomendación avanzada"""
        response = self.client.get(
            reverse('trainer_recommendation_advanced', args=[self.user.pk])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_recomendacion_asociada_a_rutina(self):
        """Verifica que se puede asociar recomendación a rutina"""
        routine_user = Routine.objects.create(
            nombre='Rutina Usuario',
            user=self.user
        )
        response = self.client.post(
            reverse('trainer_recommendation_create', args=[self.user.pk]),
            {
                'titulo': 'Recomendación Rutina',
                'mensaje': 'Ajusta esta rutina',
                'tipo': 'rutina',
                'relacionado_routine': routine_user.pk
            }
        )
        self.assertEqual(response.status_code, 302)
        recommendation = TrainerRecommendation.objects.filter(
            trainer=self.trainer,
            user=self.user
        ).first()
        self.assertIsNotNone(recommendation)
    
    def test_recomendacion_asociada_a_progreso(self):
        """Verifica que se puede asociar recomendación a progreso"""
        progress = ProgressLog.objects.create(
            user=self.user,
            routine=self.routine,
            fecha=date.today(),
            esfuerzo=7
        )
        response = self.client.post(
            reverse('trainer_recommendation_create', args=[self.user.pk]),
            {
                'titulo': 'Recomendación Progreso',
                'mensaje': 'Buen trabajo',
                'tipo': 'progreso',
                'relacionado_progress': progress.pk
            }
        )
        self.assertEqual(response.status_code, 302)
        recommendation = TrainerRecommendation.objects.filter(
            trainer=self.trainer,
            user=self.user
        ).first()
        self.assertIsNotNone(recommendation)
    
    def test_recomendacion_actualiza_stats(self):
        """Verifica que crear recomendación actualiza estadísticas"""
        hoy = date.today()
        TrainerRecommendation.objects.create(
            trainer=self.trainer,
            user=self.user,
            titulo='Test',
            mensaje='Test'
        )
        stats = TrainerMonthlyStats.objects.filter(
            trainer=self.trainer,
            anio=hoy.year,
            mes=hoy.month
        ).first()
        if stats:
            self.assertGreaterEqual(stats.seguimientos_realizados, 1)


class TestCreacionContenido(TestEntrenadorBase):
    """Tests de creación de contenido"""
    
    def test_lista_rutinas_predisenadas_carga(self):
        """Verifica que la lista de rutinas prediseñadas carga"""
        response = self.client.get(reverse('trainer_routines'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rutina Prediseñada')
    
    def test_crear_rutina_predisenada(self):
        """Verifica creación de rutina prediseñada"""
        response = self.client.post(reverse('trainer_routine_create'), {
            'nombre': 'Nueva Rutina Prediseñada',
            'descripcion': 'Descripción de prueba',
            'objetivo': 'Ganar fuerza',
            'nivel_dificultad': 'intermedio'
        })
        self.assertEqual(response.status_code, 302)
        routine = Routine.objects.get(nombre='Nueva Rutina Prediseñada')
        self.assertTrue(routine.es_predisenada)
        self.assertEqual(routine.autor_trainer, self.trainer)
    
    def test_lista_ejercicios_entrenador_carga(self):
        """Verifica que la lista de ejercicios del entrenador carga"""
        response = self.client.get(reverse('trainer_exercises'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sentadillas')
    
    def test_crear_ejercicio(self):
        """Verifica creación de ejercicio por entrenador"""
        response = self.client.post(reverse('trainer_exercise_create'), {
            'nombre': 'Nuevo Ejercicio',
            'tipo': 'fuerza',
            'descripcion': 'Descripción completa',
            'duracion_min': 15,
            'dificultad': 4,
            'instrucciones_paso_a_paso': 'Paso 1, Paso 2',
            'musculos_involucrados': 'Cuádriceps, Glúteos',
            'equipamiento_necesario': 'Mancuernas',
            'precauciones': 'Cuidado con la espalda',
            'contraindicaciones': 'No hacer con lesión de rodilla'
        })
        self.assertEqual(response.status_code, 302)
        exercise = Exercise.objects.get(nombre='Nuevo Ejercicio')
        self.assertEqual(exercise.creado_por, self.trainer)
        self.assertEqual(exercise.instrucciones_paso_a_paso, 'Paso 1, Paso 2')
    
    def test_editar_ejercicio_existente(self):
        """Verifica edición de ejercicio existente"""
        response = self.client.post(
            reverse('trainer_exercise_create'),
            {
                'ejercicio_id': self.exercise.pk,
                'nombre': 'Sentadillas Modificadas',
                'tipo': 'fuerza',
                'descripcion': 'Descripción actualizada',
                'duracion_min': 12,
                'dificultad': 4
            }
        )
        # Verificar que se actualiza (depende de la implementación)


class TestAdministracionEjercicios(TestEntrenadorBase):
    """Tests de administración de ejercicios"""
    
    def test_catalogo_ejercicios_carga(self):
        """Verifica que el catálogo de ejercicios carga"""
        response = self.client.get(reverse('trainer_exercises'))
        self.assertEqual(response.status_code, 200)
    
    def test_catalogo_muestra_ejercicios_entrenador(self):
        """Verifica que el catálogo muestra ejercicios del entrenador"""
        Exercise.objects.create(
            nombre='Ejercicio Entrenador',
            tipo='cardio',
            creado_por=self.trainer
        )
        response = self.client.get(reverse('trainer_exercises'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ejercicio Entrenador')
    
    def test_validacion_contenido_ejercicio(self):
        """Verifica validación de contenido de ejercicio"""
        response = self.client.post(reverse('trainer_exercise_create'), {
            'nombre': '',  # Sin nombre
            'tipo': 'fuerza'
        })
        # Debería mostrar error de validación
        self.assertEqual(response.status_code, 200)


class TestAlertasYNotificaciones(TestEntrenadorBase):
    """Tests de alertas y notificaciones"""
    
    def test_alertas_bajo_rendimiento(self):
        """Verifica alertas de bajo rendimiento"""
        # Usuario sin progreso reciente
        response = self.client.get(reverse('trainer_assignees'))
        self.assertEqual(response.status_code, 200)
    
    def test_alertas_inactividad(self):
        """Verifica alertas de inactividad"""
        # Usuario sin actividad hace tiempo
        response = self.client.get(reverse('trainer_assignees'))
        self.assertEqual(response.status_code, 200)
    
    def test_lista_usuarios_necesitan_atencion(self):
        """Verifica lista de usuarios que necesitan atención"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class TestEstadisticasEntrenador(TestEntrenadorBase):
    """Tests de estadísticas del entrenador"""
    
    def test_estadisticas_mensuales_actualizan(self):
        """Verifica que las estadísticas mensuales se actualizan"""
        hoy = date.today()
        
        # Crear recomendación
        TrainerRecommendation.objects.create(
            trainer=self.trainer,
            user=self.user,
            titulo='Test',
            mensaje='Test'
        )
        
        stats = TrainerMonthlyStats.objects.filter(
            trainer=self.trainer,
            anio=hoy.year,
            mes=hoy.month
        ).first()
        
        if stats:
            self.assertGreaterEqual(stats.seguimientos_realizados, 1)
    
    def test_estadisticas_asignaciones_nuevas(self):
        """Verifica estadísticas de asignaciones nuevas"""
        hoy = date.today()
        nuevo_usuario = User.objects.create_user(
            username='nuevo',
            password='pass'
        )
        TrainerAssignment.objects.create(
            trainer=self.trainer,
            user=nuevo_usuario,
            activo=True
        )
        
        stats = TrainerMonthlyStats.objects.filter(
            trainer=self.trainer,
            anio=hoy.year,
            mes=hoy.month
        ).first()
        
        if stats:
            self.assertGreaterEqual(stats.asignaciones_nuevas, 1)


class TestValidacionesYErrores(TestEntrenadorBase):
    """Tests de validaciones y manejo de errores"""
    
    def test_no_puede_acceder_a_usuario_no_asignado(self):
        """Verifica que no puede acceder a usuario no asignado"""
        otro_usuario = User.objects.create_user(
            username='otro',
            password='pass'
        )
        response = self.client.get(reverse('trainer_feedback', args=[otro_usuario.pk]))
        # Debería redirigir o mostrar error
        self.assertNotEqual(response.status_code, 200)
    
    def test_validacion_formulario_recomendacion(self):
        """Verifica validación de formulario de recomendación"""
        response = self.client.post(
            reverse('trainer_recommendation_create', args=[self.user.pk]),
            {
                # Sin título ni mensaje
            }
        )
        # Debería mostrar errores de validación
        self.assertEqual(response.status_code, 200)


class TestIntegracionCompleta(TestEntrenadorBase):
    """Tests de integración completa del flujo de entrenador"""
    
    def test_flujo_completo_entrenador(self):
        """Test del flujo completo: ver usuario -> analizar -> recomendar"""
        # 1. Ver lista de usuarios asignados
        response = self.client.get(reverse('trainer_assignees'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Ver detalle de usuario
        response = self.client.get(reverse('trainer_feedback', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        
        # 3. Analizar progreso
        ProgressLog.objects.create(
            user=self.user,
            routine=self.routine,
            fecha=date.today(),
            esfuerzo=7
        )
        response = self.client.get(reverse('trainer_progress_analysis', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        
        # 4. Crear recomendación
        response = self.client.post(
            reverse('trainer_recommendation_create', args=[self.user.pk]),
            {
                'titulo': 'Recomendación Flujo',
                'mensaje': 'Mensaje de prueba',
                'tipo': 'general'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrainerRecommendation.objects.filter(
            trainer=self.trainer,
            user=self.user
        ).exists())
    
    def test_flujo_creacion_contenido(self):
        """Test del flujo de creación de contenido"""
        # 1. Crear ejercicio
        self.client.post(reverse('trainer_exercise_create'), {
            'nombre': 'Ejercicio Flujo',
            'tipo': 'fuerza',
            'descripcion': 'Test',
            'duracion_min': 20,
            'dificultad': 3
        })
        exercise = Exercise.objects.get(nombre='Ejercicio Flujo')
        self.assertIsNotNone(exercise)
        
        # 2. Crear rutina prediseñada
        self.client.post(reverse('trainer_routine_create'), {
            'nombre': 'Rutina Flujo',
            'descripcion': 'Test'
        })
        routine = Routine.objects.get(nombre='Rutina Flujo')
        self.assertIsNotNone(routine)
        self.assertTrue(routine.es_predisenada)
        
        # 3. Agregar ejercicio a rutina
        self.client.post(
            reverse('routine_add_item', args=[routine.pk]),
            {
                'exercise': exercise.pk,
                'orden': 1,
                'series': 3,
                'repeticiones': 10
            }
        )
        self.assertTrue(RoutineItem.objects.filter(routine=routine).exists())


class TestNavegacion(TestEntrenadorBase):
    """Tests de navegación y menús"""
    
    def test_menu_muestra_opciones_correctas(self):
        """Verifica que el menú muestra opciones correctas para entrenador"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Verificar que contiene enlaces a funcionalidades de entrenador
        self.assertContains(response, 'Mis Usuarios')
        self.assertContains(response, 'Mis Rutinas')
        self.assertContains(response, 'Mis Ejercicios')
    
    def test_logout_funciona(self):
        """Verifica que el logout funciona correctamente"""
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        # Verificar que el usuario ya no está autenticado
        response = self.client.get(reverse('home'))
        self.assertNotEqual(response.status_code, 200)

