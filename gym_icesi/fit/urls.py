# fit/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.home, name="home"),

    # Rutinas
    path("rutinas/", views.routine_list, name="routine_list"),
    path("rutinas/nueva/", views.routine_create, name="routine_create"),
    path("rutinas/<int:pk>/", views.routine_detail, name="routine_detail"),
    path("rutinas/<int:pk>/agregar-item/", views.routine_add_item, name="routine_add_item"),
    path("rutinas/<int:pk>/adoptar/", views.routine_adopt, name="routine_adopt"),

    # Progreso
    path("progreso/nuevo/", views.progress_create, name="progress_create"),

    # Módulo entrenador (para entrenadores internos)
    path("trainer/asignados/", views.trainer_assignees, name="trainer_assignees"),
    path("trainer/feedback/<int:user_id>/", views.trainer_feedback, name="trainer_feedback"),

    # Listado institucional de entrenadores (modo admin)
    path("entrenadores/", views.trainers_list, name="trainers_list"),
    path("entrenadores/info/", views.trainers_view, name="trainers_view"),
    path("entrenadores/<str:emp_id>/", views.trainer_detail, name="trainer_detail"),

    # Reportes
    path("reportes/adherencia/", views.report_adherence, name="report_adherence"),
    path("reportes/carga/", views.report_load_balance, name="report_load_balance"),

    # Admin: asignar entrenador y recalcular stats
    path("admin/asignar-entrenador/", views.admin_assign_trainer, name="admin_assign_trainer"),
    path("admin/recalc-stats/", views.recalc_stats_month, name="recalc_stats_month"),
]
