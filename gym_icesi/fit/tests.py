"""
Tests completos para verificar todas las funcionalidades del sistema Gym Icesi
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from fit.models import (
    Exercise, Routine, RoutineItem, ProgressLog,
    TrainerAssignment, UserMonthlyStats, TrainerMonthlyStats,
    TrainerRecommendation
)
from fit.institutional_models import InstitutionalUser


class AuthenticationTests(TestCase):
    """Tests de autenticación institucional"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
    
    def test_login_page_loads(self):
        """Verifica que la página de login carga correctamente"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar Sesión')
    
    def test_login_with_invalid_credentials(self):
        """Verifica que login con credenciales inválidas muestra error"""
        response = self.client.post(reverse('login'), {
            'username': 'usuario_inexistente',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incorrectos', status_code=200)


class ExerciseTests(TestCase):
    """Tests de gestión de ejercicios"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
    
    def test_create_exercise(self):
        """Verifica creación de ejercicio personalizado"""
        response = self.client.post(reverse('exercise_create'), {
            'nombre': 'Test Exercise',
            'tipo': 'Cardio',
            'descripcion': 'Test description',
            'duracion_min': 30,
            'dificultad': 3
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Exercise.objects.filter(nombre='Test Exercise').exists())
    
    def test_exercise_list_view(self):
        """Verifica que la vista de ejercicios funciona"""
        Exercise.objects.create(
            nombre='Test Exercise',
            tipo='Cardio',
            descripcion='Test',
            duracion_min=30,
            dificultad=3,
            creado_por=self.user,
            es_personalizado=True
        )
        response = self.client.get(reverse('trainer_exercises'))
        self.assertEqual(response.status_code, 200)


class RoutineTests(TestCase):
    """Tests de gestión de rutinas"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        self.exercise = Exercise.objects.create(
            nombre='Test Exercise',
            tipo='Cardio',
            descripcion='Test',
            duracion_min=30,
            dificultad=3
        )
    
    def test_create_routine(self):
        """Verifica creación de rutina"""
        response = self.client.post(reverse('routine_create'), {
            'nombre': 'Test Routine',
            'descripcion': 'Test description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Routine.objects.filter(nombre='Test Routine').exists())
    
    def test_add_item_to_routine(self):
        """Verifica agregar ejercicio a rutina"""
        routine = Routine.objects.create(
            nombre='Test Routine',
            user=self.user
        )
        response = self.client.post(reverse('routine_add_item', args=[routine.pk]), {
            'exercise': self.exercise.pk,
            'orden': 1,
            'series': 3,
            'reps': 10
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RoutineItem.objects.filter(routine=routine).exists())
    
    def test_routine_list_view(self):
        """Verifica vista de lista de rutinas"""
        Routine.objects.create(nombre='Test Routine', user=self.user)
        response = self.client.get(reverse('routine_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Routine')
    
    def test_routine_detail_view(self):
        """Verifica vista de detalle de rutina"""
        routine = Routine.objects.create(nombre='Test Routine', user=self.user)
        response = self.client.get(reverse('routine_detail', args=[routine.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Routine')


class ProgressTests(TestCase):
    """Tests de registro de progreso"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        self.exercise = Exercise.objects.create(
            nombre='Test Exercise',
            tipo='Cardio',
            descripcion='Test',
            duracion_min=30,
            dificultad=3
        )
        self.routine = Routine.objects.create(
            nombre='Test Routine',
            user=self.user
        )
        RoutineItem.objects.create(
            routine=self.routine,
            exercise=self.exercise,
            orden=1
        )
    
    def test_create_progress(self):
        """Verifica registro de progreso"""
        response = self.client.post(reverse('progress_create'), {
            'routine': self.routine.pk,
            'fecha': date.today(),
            'esfuerzo': 7
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProgressLog.objects.filter(user=self.user).exists())
    
    def test_progress_updates_stats(self):
        """Verifica que el progreso actualiza estadísticas"""
        hoy = date.today()
        ProgressLog.objects.create(
            user=self.user,
            routine=self.routine,
            fecha=hoy,
            esfuerzo=7
        )
        stats = UserMonthlyStats.objects.filter(
            user=self.user,
            anio=hoy.year,
            mes=hoy.month
        ).first()
        self.assertIsNotNone(stats)
        self.assertEqual(stats.seguimientos_registrados, 1)


class TrainerTests(TestCase):
    """Tests de funcionalidades de entrenadores"""
    
    def setUp(self):
        self.trainer = User.objects.create_user(
            username='trainer',
            password='testpass',
            is_staff=True
        )
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='trainer', password='testpass')
    
    def test_trainer_create_preset_routine(self):
        """Verifica que entrenador puede crear rutina prediseñada"""
        response = self.client.post(reverse('trainer_routine_create'), {
            'nombre': 'Preset Routine',
            'descripcion': 'Test preset'
        })
        self.assertEqual(response.status_code, 302)
        routine = Routine.objects.get(nombre='Preset Routine')
        self.assertTrue(routine.es_predisenada)
        self.assertEqual(routine.autor_trainer, self.trainer)
    
    def test_trainer_create_exercise(self):
        """Verifica que entrenador puede registrar ejercicio"""
        response = self.client.post(reverse('trainer_exercise_create'), {
            'nombre': 'Trainer Exercise',
            'tipo': 'Fuerza',
            'descripcion': 'Test',
            'duracion_min': 45,
            'dificultad': 4
        })
        self.assertEqual(response.status_code, 302)
        exercise = Exercise.objects.get(nombre='Trainer Exercise')
        self.assertEqual(exercise.creado_por, self.trainer)
    
    def test_trainer_assign_user(self):
        """Verifica asignación de usuario a entrenador"""
        assignment = TrainerAssignment.objects.create(
            trainer=self.trainer,
            user=self.user,
            activo=True
        )
        self.assertTrue(assignment.activo)
        self.assertEqual(assignment.trainer, self.trainer)
        self.assertEqual(assignment.user, self.user)
    
    def test_trainer_create_recommendation(self):
        """Verifica que entrenador puede crear recomendación"""
        TrainerAssignment.objects.create(
            trainer=self.trainer,
            user=self.user,
            activo=True
        )
        response = self.client.post(
            reverse('trainer_recommendation_create', args=[self.user.pk]),
            {'mensaje': 'Test recommendation'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TrainerRecommendation.objects.filter(
                trainer=self.trainer,
                user=self.user
            ).exists()
        )


class RoutineAdoptionTests(TestCase):
    """Tests de adopción de rutinas prediseñadas"""
    
    def setUp(self):
        self.trainer = User.objects.create_user(
            username='trainer',
            password='testpass',
            is_staff=True
        )
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='user', password='testpass')
        
        # Crear rutina prediseñada
        self.preset_routine = Routine.objects.create(
            nombre='Preset Routine',
            user=self.trainer,
            es_predisenada=True,
            autor_trainer=self.trainer
        )
    
    def test_adopt_preset_routine(self):
        """Verifica adopción de rutina prediseñada"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('routine_adopt', args=[self.preset_routine.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó una copia para el usuario
        user_routine = Routine.objects.filter(
            user=self.user,
            nombre='Preset Routine'
        ).first()
        self.assertIsNotNone(user_routine)
        self.assertFalse(user_routine.es_predisenada)
        self.assertNotEqual(user_routine.pk, self.preset_routine.pk)


class ReportsTests(TestCase):
    """Tests de reportes"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        
        # Crear datos de prueba
        self.routine = Routine.objects.create(nombre='Test Routine', user=self.user)
        self.exercise = Exercise.objects.create(
            nombre='Test Exercise',
            tipo='Cardio',
            descripcion='Test',
            duracion_min=30,
            dificultad=3
        )
        RoutineItem.objects.create(
            routine=self.routine,
            exercise=self.exercise,
            orden=1
        )
        
        # Crear progresos
        hoy = date.today()
        for i in range(5):
            ProgressLog.objects.create(
                user=self.user,
                routine=self.routine,
                fecha=hoy - timedelta(days=i),
                esfuerzo=7 + i
            )
    
    def test_adherence_report(self):
        """Verifica reporte de adherencia"""
        response = self.client.get(reverse('report_adherence'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Adherencia')
    
    def test_load_balance_report(self):
        """Verifica reporte de balance de carga"""
        response = self.client.get(reverse('report_load_balance'))
        self.assertEqual(response.status_code, 200)
    
    def test_progress_trend_report(self):
        """Verifica reporte de tendencias"""
        response = self.client.get(reverse('report_progress_trend'))
        self.assertEqual(response.status_code, 200)
    
    def test_achievements_report(self):
        """Verifica reporte de logros"""
        response = self.client.get(reverse('report_achievements'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logros')


class StatisticsTests(TestCase):
    """Tests de estadísticas mensuales"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.trainer = User.objects.create_user(
            username='trainer',
            password='testpass',
            is_staff=True
        )
        self.routine = Routine.objects.create(nombre='Test Routine', user=self.user)
    
    def test_user_stats_creation(self):
        """Verifica creación de estadísticas de usuario"""
        hoy = date.today()
        stats = UserMonthlyStats.objects.create(
            user=self.user,
            anio=hoy.year,
            mes=hoy.month,
            rutinas_iniciadas=1,
            seguimientos_registrados=5
        )
        self.assertEqual(stats.rutinas_iniciadas, 1)
        self.assertEqual(stats.seguimientos_registrados, 5)
    
    def test_trainer_stats_creation(self):
        """Verifica creación de estadísticas de entrenador"""
        hoy = date.today()
        stats = TrainerMonthlyStats.objects.create(
            trainer=self.trainer,
            anio=hoy.year,
            mes=hoy.month,
            asignaciones_nuevas=2,
            seguimientos_realizados=3
        )
        self.assertEqual(stats.asignaciones_nuevas, 2)
        self.assertEqual(stats.seguimientos_realizados, 3)


class IntegrationTests(TestCase):
    """Tests de integración end-to-end"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
    
    def test_complete_workflow(self):
        """Test del flujo completo: crear ejercicio -> rutina -> progreso"""
        # 1. Crear ejercicio
        self.client.post(reverse('exercise_create'), {
            'nombre': 'Workflow Exercise',
            'tipo': 'Cardio',
            'descripcion': 'Test',
            'duracion_min': 30,
            'dificultad': 3
        })
        exercise = Exercise.objects.get(nombre='Workflow Exercise')
        
        # 2. Crear rutina
        self.client.post(reverse('routine_create'), {
            'nombre': 'Workflow Routine',
            'descripcion': 'Test'
        })
        routine = Routine.objects.get(nombre='Workflow Routine')
        
        # 3. Agregar ejercicio a rutina
        self.client.post(reverse('routine_add_item', args=[routine.pk]), {
            'exercise': exercise.pk,
            'orden': 1,
            'series': 3,
            'reps': 10
        })
        
        # 4. Registrar progreso
        self.client.post(reverse('progress_create'), {
            'routine': routine.pk,
            'fecha': date.today(),
            'esfuerzo': 8
        })
        
        # Verificar que todo se creó correctamente
        self.assertTrue(Exercise.objects.filter(nombre='Workflow Exercise').exists())
        self.assertTrue(Routine.objects.filter(nombre='Workflow Routine').exists())
        self.assertTrue(RoutineItem.objects.filter(routine=routine).exists())
        self.assertTrue(ProgressLog.objects.filter(user=self.user).exists())
