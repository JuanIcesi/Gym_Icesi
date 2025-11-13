# fit/signals.py
"""
Señales Django para actualización automática de estadísticas
"""
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Routine, ProgressLog, TrainerAssignment, TrainerRecommendation
from .views import update_user_stats, update_trainer_stats


@receiver(post_save, sender=Routine)
def routine_saved(sender, instance, created, **kwargs):
    """Actualiza estadísticas cuando se crea una rutina"""
    if created:
        hoy = date.today()
        update_user_stats(instance.user, hoy.year, hoy.month)


@receiver(post_save, sender=ProgressLog)
def progress_saved(sender, instance, created, **kwargs):
    """Actualiza estadísticas cuando se registra progreso"""
    if created:
        update_user_stats(instance.user, instance.fecha.year, instance.fecha.month)


@receiver(post_save, sender=TrainerAssignment)
def assignment_saved(sender, instance, created, **kwargs):
    """Actualiza estadísticas cuando se asigna un entrenador"""
    if created:
        hoy = date.today()
        update_trainer_stats(instance.trainer, hoy.year, hoy.month)


@receiver(post_save, sender=TrainerRecommendation)
def recommendation_saved(sender, instance, created, **kwargs):
    """Actualiza estadísticas cuando un entrenador da una recomendación"""
    if created:
        hoy = date.today()
        update_trainer_stats(instance.trainer, hoy.year, hoy.month)

