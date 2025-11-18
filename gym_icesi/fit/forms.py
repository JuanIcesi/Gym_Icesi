from django import forms
from .models import Routine, RoutineItem, ProgressLog, Exercise, TrainerRecommendation, UserProfile, Message, EventoInstitucional, InscripcionEvento, EspacioDeportivo, ReservaEspacio

class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ['nombre', 'descripcion', 'frecuencia', 'dias_semana', 'meta_personal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la rutina'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción de la rutina (opcional)'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'dias_semana': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: L,M,J,V (Lunes, Martes, Jueves, Viernes)'}),
            'meta_personal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Metas personales para esta rutina (opcional)'}),
        }

class RoutineItemForm(forms.ModelForm):
    class Meta:
        model = RoutineItem
        fields = ['exercise','orden','series','reps','tiempo_seg','notas']
        widgets = {
            'exercise': forms.Select(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'series': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reps': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tiempo_seg': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notas opcionales'}),
        }

class ProgressForm(forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = ['routine','fecha','repeticiones','tiempo_seg','esfuerzo','peso_usado','notas']
        widgets = {
            'routine': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'repeticiones': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tiempo_seg': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'esfuerzo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'peso_usado': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.1, 'placeholder': 'Peso en kg (opcional)'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['nombre', 'tipo', 'descripcion', 'duracion_min', 'dificultad', 'video_url',
                  'instrucciones_paso_a_paso', 'musculos_involucrados', 'equipamiento_necesario',
                  'precauciones', 'contraindicaciones', 'variaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del ejercicio'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción general del ejercicio'}),
            'duracion_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'dificultad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL del video (opcional)'}),
            'instrucciones_paso_a_paso': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Instrucciones detalladas paso a paso...'}),
            'musculos_involucrados': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cuádriceps, Glúteos, Isquiotibiales'}),
            'equipamiento_necesario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mancuernas, Banco, Barra'}),
            'precauciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Precauciones importantes...'}),
            'contraindicaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contraindicaciones médicas...'}),
            'variaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Variaciones del ejercicio...'}),
        }

class TrainerRecommendationForm(forms.ModelForm):
    class Meta:
        model = TrainerRecommendation
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escribe tu recomendación o feedback...'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['peso_kg', 'altura_cm', 'condiciones_medicas']
        widgets = {
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.1, 'placeholder': 'Peso en kilogramos'}),
            'altura_cm': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Altura en centímetros'}),
            'condiciones_medicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Condiciones médicas o lesiones conocidas (opcional)'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinatario', 'asunto', 'mensaje', 'relacionado_routine', 'relacionado_progress']
        widgets = {
            'destinatario': forms.Select(attrs={'class': 'form-control'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto del mensaje'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escribe tu mensaje...'}),
            'relacionado_routine': forms.Select(attrs={'class': 'form-control'}),
            'relacionado_progress': forms.Select(attrs={'class': 'form-control'}),
        }

class ReservaEspacioForm(forms.ModelForm):
    class Meta:
        model = ReservaEspacio
        fields = ['espacio', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'notas']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-control'}),
            'fecha_reserva': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }
