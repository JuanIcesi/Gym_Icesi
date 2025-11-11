from django.contrib import admin
from .models import Exercise, Routine, RoutineItem, TrainerAssignment, ProgressLog, UserMonthlyStats, TrainerMonthlyStats

class RoutineItemInline(admin.TabularInline):
    model = RoutineItem
    extra = 0

@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ('nombre','user','es_predisenada','autor_trainer','fecha_creacion')
    inlines = [RoutineItemInline]
    search_fields = ('nombre','user__username')

admin.site.register([Exercise, TrainerAssignment, ProgressLog, UserMonthlyStats, TrainerMonthlyStats])
