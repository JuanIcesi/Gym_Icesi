from django.db import models
from django.contrib.auth.models import User

class Exercise(models.Model):
    TIPO = [('cardio','Cardio'), ('fuerza','Fuerza'), ('movilidad','Movilidad')]
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=12, choices=TIPO)
    descripcion = models.TextField(blank=True)
    duracion_min = models.PositiveIntegerField(default=0)
    dificultad = models.PositiveSmallIntegerField(default=1)  # 1-5
    video_url = models.URLField(blank=True)
    creado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='exercises_created')
    es_personalizado = models.BooleanField(default=False)  # True si fue creado por usuario/entrenador
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self): return self.nombre

class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    es_predisenada = models.BooleanField(default=False)
    autor_trainer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='routines_autor')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.nombre} ({self.user.username})'

class RoutineItem(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='items')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    orden = models.PositiveIntegerField(default=1)
    series = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    tiempo_seg = models.PositiveIntegerField(null=True, blank=True)
    notas = models.CharField(max_length=255, blank=True)
    class Meta:
        ordering = ['orden']

class TrainerAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_assignment_user')
    trainer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='trainer_assignment_trainer')
    fecha_asignacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    class Meta:
        unique_together = [('user','trainer','activo')]

class ProgressLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='progress')
    fecha = models.DateField()
    repeticiones = models.PositiveIntegerField(null=True, blank=True)
    tiempo_seg = models.PositiveIntegerField(null=True, blank=True)
    esfuerzo = models.PositiveSmallIntegerField(default=5)  # 1-10
    notas = models.TextField(blank=True)
    class Meta:
        indexes = [models.Index(fields=['user','fecha'])]

class UserMonthlyStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anio = models.PositiveIntegerField()
    mes = models.PositiveSmallIntegerField()  # 1-12
    rutinas_iniciadas = models.PositiveIntegerField(default=0)
    seguimientos_registrados = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = [('user','anio','mes')]

class TrainerMonthlyStats(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    anio = models.PositiveIntegerField()
    mes = models.PositiveSmallIntegerField()
    asignaciones_nuevas = models.PositiveIntegerField(default=0)
    seguimientos_realizados = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = [('trainer','anio','mes')]

class TrainerRecommendation(models.Model):
    """Recomendaciones y feedback de entrenadores a usuarios"""
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations_given')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations_received')
    routine = models.ForeignKey(Routine, null=True, blank=True, on_delete=models.SET_NULL, related_name='recommendations')
    progress_log = models.ForeignKey(ProgressLog, null=True, blank=True, on_delete=models.SET_NULL, related_name='recommendations')
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    class Meta:
        ordering = ['-fecha']