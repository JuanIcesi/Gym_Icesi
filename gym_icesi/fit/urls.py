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
]
