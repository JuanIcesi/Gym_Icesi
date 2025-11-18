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
    # Campos adicionales para entrenadores
    instrucciones_paso_a_paso = models.TextField(blank=True, help_text="Instrucciones detalladas paso a paso para realizar el ejercicio")
    musculos_involucrados = models.CharField(max_length=500, blank=True, help_text="Músculos principales involucrados (separados por comas)")
    equipamiento_necesario = models.CharField(max_length=500, blank=True, help_text="Equipamiento necesario (separado por comas)")
    precauciones = models.TextField(blank=True, help_text="Precauciones importantes al realizar este ejercicio")
    contraindicaciones = models.TextField(blank=True, help_text="Contraindicaciones médicas o situaciones donde no se debe realizar")
    variaciones = models.TextField(blank=True, help_text="Variaciones del ejercicio (principiante, intermedio, avanzado)")
    def __str__(self): return self.nombre

class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    es_predisenada = models.BooleanField(default=False)
    autor_trainer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='routines_autor')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Nuevos campos para frecuencia y metas
    frecuencia = models.CharField(max_length=20, choices=[('diaria', 'Diaria'), ('semanal', 'Semanal'), ('personalizada', 'Personalizada')], default='semanal', blank=True)
    dias_semana = models.CharField(max_length=50, blank=True, help_text="Días de la semana separados por comas (ej: L,M,J,V)")
    meta_personal = models.TextField(blank=True, help_text="Metas personales para esta rutina")
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
    peso_usado = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Peso utilizado en kilogramos")
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

class UserProfile(models.Model):
    """Perfil de salud del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Peso en kilogramos")
    altura_cm = models.PositiveIntegerField(null=True, blank=True, help_text="Altura en centímetros")
    condiciones_medicas = models.TextField(blank=True, help_text="Condiciones médicas o lesiones conocidas")
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'Perfil de {self.user.username}'

class Message(models.Model):
    """Sistema de mensajería entre usuarios y entrenadores"""
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_received')
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    relacionado_routine = models.ForeignKey(Routine, null=True, blank=True, on_delete=models.SET_NULL)
    relacionado_progress = models.ForeignKey(ProgressLog, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        ordering = ['-fecha']

class EventoInstitucional(models.Model):
    """Calendario de eventos y talleres"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    tipo = models.CharField(max_length=50, choices=[('taller', 'Taller'), ('evento', 'Evento'), ('clase', 'Clase'), ('otro', 'Otro')])
    ubicacion = models.CharField(max_length=200, blank=True)
    capacidad_maxima = models.PositiveIntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.titulo

class InscripcionEvento(models.Model):
    """Inscripciones de usuarios a eventos"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_inscritos')
    evento = models.ForeignKey(EventoInstitucional, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    asistio = models.BooleanField(default=False)
    class Meta:
        unique_together = [('usuario', 'evento')]

class EspacioDeportivo(models.Model):
    """Espacios deportivos disponibles para reserva"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=100, choices=[('gimnasio', 'Gimnasio'), ('cancha', 'Cancha'), ('piscina', 'Piscina'), ('salon', 'Salón'), ('otro', 'Otro')])
    capacidad = models.PositiveIntegerField(null=True, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    def __str__(self): return self.nombre

class ReservaEspacio(models.Model):
    """Reservas de espacios deportivos"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    espacio = models.ForeignKey(EspacioDeportivo, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')], default='pendiente')
    notas = models.TextField(blank=True)
    class Meta:
        ordering = ['fecha_reserva', 'hora_inicio']

class AssignmentHistory(models.Model):
    """Historial de cambios en asignaciones de entrenadores"""
    assignment = models.ForeignKey(TrainerAssignment, on_delete=models.CASCADE, related_name='history')
    accion = models.CharField(max_length=50, choices=[('creada', 'Asignación Creada'), ('modificada', 'Asignación Modificada'), ('desactivada', 'Asignación Desactivada'), ('reactivada', 'Asignación Reactivada')])
    administrador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignment_changes')
    fecha = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)
    class Meta:
        ordering = ['-fecha']

class ContentModeration(models.Model):
    """Moderación de contenido (ejercicios y rutinas)"""
    ESTADO_CHOICES = [('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado'), ('editado', 'Editado')]
    tipo_contenido = models.CharField(max_length=20, choices=[('exercise', 'Ejercicio'), ('routine', 'Rutina')])
    contenido_id = models.PositiveIntegerField()  # ID del ejercicio o rutina
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    moderador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderations')
    fecha_revision = models.DateTimeField(null=True, blank=True)
    comentarios = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-fecha_creacion']

class SystemConfig(models.Model):
    """Configuración global del sistema"""
    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    descripcion = models.TextField(blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.clave} = {self.valor}'