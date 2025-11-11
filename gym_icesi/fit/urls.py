from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Rutinas (usuario)
    path('routines/', views.routine_list, name='routine_list'),
    path('routines/new/', views.routine_create, name='routine_create'),
    path('routines/<int:pk>/', views.routine_detail, name='routine_detail'),
    path('routines/<int:pk>/add-item/', views.routine_add_item, name='routine_add_item'),
    path('routines/<int:pk>/adopt/', views.routine_adopt, name='routine_adopt'),

    # Progreso
    path('progress/new/', views.progress_create, name='progress_create'),

    # Entrenador
    path('trainer/assignees/', views.trainer_assignees, name='trainer_assignees'),
    path('trainer/feedback/<int:user_id>/', views.trainer_feedback, name='trainer_feedback'),

    # Admin simple
    path('adminx/assign/', views.admin_assign_trainer, name='admin_assign_trainer'),

    # Reportes
    path('reports/adherence/', views.report_adherence, name='report_adherence'),
    path('reports/load-balance/', views.report_load_balance, name='report_load_balance'),

    # Stats (recalcular)
    path('adminx/recalc-stats/', views.recalc_stats_month, name='recalc_stats_month'),
]
