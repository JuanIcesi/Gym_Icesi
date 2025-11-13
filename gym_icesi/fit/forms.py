from django import forms
from .models import Routine, RoutineItem, ProgressLog, Exercise, TrainerRecommendation

class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la rutina'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción de la rutina (opcional)'}),
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
        fields = ['routine','fecha','repeticiones','tiempo_seg','esfuerzo','notas']
        widgets = {
            'routine': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'repeticiones': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tiempo_seg': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'esfuerzo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['nombre', 'tipo', 'descripcion', 'duracion_min', 'dificultad', 'video_url']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del ejercicio'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del ejercicio'}),
            'duracion_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'dificultad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL del video (opcional)'}),
        }

class TrainerRecommendationForm(forms.ModelForm):
    class Meta:
        model = TrainerRecommendation
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escribe tu recomendación o feedback...'}),
        }
