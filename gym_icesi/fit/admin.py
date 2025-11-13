# fit/admin.py
from django.contrib import admin

from fit.institutional_models import Employee, InstitutionalUser


from .models import (
    Exercise,
    Routine,
    RoutineItem,
    TrainerAssignment,
    ProgressLog,
    UserMonthlyStats,
    TrainerMonthlyStats,
    TrainerRecommendation,
)

# ----------------------------------------------------
# Inline: ítems dentro de la rutina
# ----------------------------------------------------
class RoutineItemInline(admin.TabularInline):
    model = RoutineItem
    extra = 0
    autocomplete_fields = ['exercise']
    show_change_link = True


# ----------------------------------------------------
# Admin de Rutinas
# ----------------------------------------------------
@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user', 'es_predisenada', 'autor_trainer', 'fecha_creacion')
    list_filter = ('es_predisenada', 'fecha_creacion')
    search_fields = ('nombre', 'user__username', 'autor_trainer__username')
    inlines = [RoutineItemInline]
    ordering = ('-fecha_creacion',)
    date_hierarchy = 'fecha_creacion'


# ----------------------------------------------------
# Admin de Ejercicios
# ----------------------------------------------------
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'descripcion')
    search_fields = ('nombre', 'tipo')


# ----------------------------------------------------
# Admin de Asignaciones de Entrenador
# ----------------------------------------------------
@admin.register(TrainerAssignment)
class TrainerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'user', 'fecha_asignacion')
    list_filter = ('fecha_asignacion',)
    search_fields = ('trainer__username', 'user__username')


# ----------------------------------------------------
# Admin de Registros de Progreso
# ----------------------------------------------------
@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'routine', 'fecha', 'esfuerzo')
    list_filter = ('fecha',)
    search_fields = ('user__username', 'routine__nombre')
    ordering = ('-fecha',)


# ----------------------------------------------------
# Admin de Estadísticas Mensuales (Usuarios)
# ----------------------------------------------------
@admin.register(UserMonthlyStats)
class UserMonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'mes')
    list_filter = ('mes',)
    search_fields = ('user__username',)


# ----------------------------------------------------
# Admin de Estadísticas Mensuales (Entrenadores)
# ----------------------------------------------------
@admin.register(TrainerMonthlyStats)
class TrainerMonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'mes')
    list_filter = ('mes',)
    search_fields = ('trainer__username',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'employee_type', 'faculty_code')
    search_fields = ('first_name', 'last_name', 'employee_type')
    list_filter = ('employee_type', 'faculty_code')
    ordering = ('last_name',)


@admin.register(InstitutionalUser)
class InstitutionalUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_active', 'student_id', 'employee_id')
    search_fields = ('username', 'role')
    list_filter = ('role', 'is_active')


@admin.register(TrainerRecommendation)
class TrainerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'user', 'fecha', 'leido')
    list_filter = ('fecha', 'leido')
    search_fields = ('trainer__username', 'user__username', 'mensaje')
    ordering = ('-fecha',)