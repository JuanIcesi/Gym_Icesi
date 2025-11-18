# fit/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Página de inicio / selección de login
    path("", views.index, name="index"),
    # Dashboard (redirige según rol)
    path("home/", views.home, name="home"),

    # Rutinas
    path("rutinas/", views.routine_list, name="routine_list"),
    path("rutinas/nueva/", views.routine_create, name="routine_create"),
    path("rutinas/<int:pk>/", views.routine_detail, name="routine_detail"),
    path("rutinas/<int:pk>/agregar-item/", views.routine_add_item, name="routine_add_item"),
    path("rutinas/<int:pk>/adoptar/", views.routine_adopt, name="routine_adopt"),

    # Progreso
    path("progreso/nuevo/", views.progress_create, name="progress_create"),
    path("progreso/", views.progress_list, name="progress_list"),

    # Módulo entrenador (para entrenadores internos)
    path("trainer/asignados/", views.trainer_assignees, name="trainer_assignees"),
    path("trainer/feedback/<int:user_id>/", views.trainer_feedback, name="trainer_feedback"),
    path("trainer/rutinas/", views.trainer_routines, name="trainer_routines"),
    path("trainer/rutinas/nueva/", views.trainer_routine_create, name="trainer_routine_create"),
    path("trainer/ejercicios/", views.trainer_exercises, name="trainer_exercises"),
    path("trainer/ejercicios/nuevo/", views.trainer_exercise_create, name="trainer_exercise_create"),
    path("trainer/recomendacion/<int:user_id>/", views.trainer_recommendation_create, name="trainer_recommendation_create"),

    # Ejercicios (usuarios)
    path("ejercicios/", views.exercises_list, name="exercises_list"),
    path("ejercicios/<int:pk>/", views.exercise_detail, name="exercise_detail"),
    path("ejercicios/nuevo/", views.exercise_create, name="exercise_create"),

    # Recomendaciones (usuarios)
    path("recomendaciones/", views.recommendations_list, name="recommendations_list"),

    # Listado institucional de entrenadores (modo admin)
    path("entrenadores/", views.trainers_list, name="trainers_list"),
    path("entrenadores/info/", views.trainers_view, name="trainers_view"),
    path("entrenadores/<str:emp_id>/", views.trainer_detail, name="trainer_detail"),

    # Reportes
    path("reportes/progreso/", views.report_progress, name="report_progress"),
    path("reportes/adherencia/", views.report_adherence, name="report_adherence"),
    path("reportes/carga/", views.report_load_balance, name="report_load_balance"),
    path("reportes/tendencias/", views.report_progress_trend, name="report_progress_trend"),
    path("reportes/logros/", views.report_achievements, name="report_achievements"),

    # Admin: asignar entrenador y recalcular stats
    path("admin/asignar-entrenador/", views.admin_assign_trainer, name="admin_assign_trainer"),
    path("admin/recalc-stats/", views.recalc_stats_month, name="recalc_stats_month"),
    
    # Nuevas funcionalidades
    # Perfil de salud
    path("perfil/salud/", views.profile_health, name="profile_health"),
    
    # Mensajería
    path("mensajes/", views.messages_list, name="messages_list"),
    path("mensajes/nuevo/", views.message_create, name="message_create"),
    path("mensajes/<int:pk>/", views.message_detail, name="message_detail"),
    
    # Eventos y calendario
    path("eventos/", views.eventos_list, name="eventos_list"),
    path("eventos/<int:pk>/", views.evento_detail, name="evento_detail"),
    path("eventos/<int:pk>/inscribir/", views.evento_inscribir, name="evento_inscribir"),
    path("eventos/<int:pk>/desinscribir/", views.evento_desinscribir, name="evento_desinscribir"),
    
    # Espacios y reservas
    path("espacios/", views.espacios_list, name="espacios_list"),
    path("espacios/<int:pk>/", views.espacio_detail, name="espacio_detail"),
    path("reservas/nueva/", views.reserva_create, name="reserva_create"),
    path("reservas/nueva/<int:espacio_id>/", views.reserva_create, name="reserva_create_espacio"),
    path("reservas/", views.reservas_list, name="reservas_list"),
    path("reservas/<int:pk>/cancelar/", views.reserva_cancel, name="reserva_cancel"),
    
    # Recordatorios
    path("recordatorios/", views.routine_reminders, name="routine_reminders"),
    
    # Funcionalidades avanzadas para entrenadores
    path("trainer/analisis/<int:user_id>/", views.trainer_progress_analysis, name="trainer_progress_analysis"),
    path("trainer/recomendacion-avanzada/<int:user_id>/", views.trainer_recommendation_advanced, name="trainer_recommendation_advanced"),
    
    # Funcionalidades avanzadas para administrador
    path("admin/usuarios/", views.admin_users_management, name="admin_users_management"),
    path("admin/asignaciones/avanzado/", views.admin_assign_trainer_advanced, name="admin_assign_trainer_advanced"),
    path("admin/asignaciones/historial/", views.admin_assignment_history, name="admin_assignment_history"),
    path("admin/moderacion/", views.admin_content_moderation, name="admin_content_moderation"),
    path("admin/moderacion/<str:tipo>/<int:contenido_id>/", views.admin_moderate_content, name="admin_moderate_content"),
    path("admin/analytics/", views.admin_analytics, name="admin_analytics"),
    path("admin/config/", views.admin_system_config, name="admin_system_config"),
]
