from django import forms
from .models import Routine, RoutineItem, ProgressLog

class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ['nombre']

class RoutineItemForm(forms.ModelForm):
    class Meta:
        model = RoutineItem
        fields = ['exercise','orden','series','reps','tiempo_seg','notas']

class ProgressForm(forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = ['routine','fecha','repeticiones','tiempo_seg','esfuerzo','notas']
