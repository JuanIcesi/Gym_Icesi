# fit/management/commands/populate_exercises.py
from django.core.management.base import BaseCommand
from fit.models import Exercise

class Command(BaseCommand):
    help = 'Crea ejercicios predefinidos en el sistema'

    def handle(self, *args, **options):
        ejercicios = [
            # Cardio
            {
                'nombre': 'Correr en Treadmill',
                'tipo': 'cardio',
                'descripcion': 'Correr en cinta caminadora a ritmo constante. Ideal para mejorar resistencia cardiovascular.',
                'duracion_min': 30,
                'dificultad': 3,
                'video_url': 'https://www.youtube.com/watch?v=example1',
                'es_personalizado': False,
            },
            {
                'nombre': 'Bicicleta Estática',
                'tipo': 'cardio',
                'descripcion': 'Ejercicio cardiovascular en bicicleta estática. Ajusta la resistencia según tu nivel.',
                'duracion_min': 25,
                'dificultad': 2,
                'video_url': 'https://www.youtube.com/watch?v=example2',
                'es_personalizado': False,
            },
            {
                'nombre': 'Burpees',
                'tipo': 'cardio',
                'descripcion': 'Ejercicio completo de cuerpo que combina sentadilla, flexión y salto. Excelente para quemar calorías.',
                'duracion_min': 10,
                'dificultad': 4,
                'video_url': 'https://www.youtube.com/watch?v=example3',
                'es_personalizado': False,
            },
            {
                'nombre': 'Jumping Jacks',
                'tipo': 'cardio',
                'descripcion': 'Salto con apertura de piernas y brazos. Perfecto calentamiento cardiovascular.',
                'duracion_min': 5,
                'dificultad': 1,
                'video_url': 'https://www.youtube.com/watch?v=example4',
                'es_personalizado': False,
            },
            {
                'nombre': 'Mountain Climbers',
                'tipo': 'cardio',
                'descripcion': 'Ejercicio dinámico en posición de plancha que mejora resistencia y fuerza core.',
                'duracion_min': 10,
                'dificultad': 3,
                'video_url': 'https://www.youtube.com/watch?v=example5',
                'es_personalizado': False,
            },
            # Fuerza
            {
                'nombre': 'Sentadillas',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio fundamental para piernas y glúteos. Baja hasta que los muslos estén paralelos al suelo.',
                'duracion_min': 0,
                'dificultad': 2,
                'video_url': 'https://www.youtube.com/watch?v=example6',
                'es_personalizado': False,
            },
            {
                'nombre': 'Press de Banca',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio para pecho, hombros y tríceps. Acostado en banco, empuja la barra hacia arriba.',
                'duracion_min': 0,
                'dificultad': 4,
                'video_url': 'https://www.youtube.com/watch?v=example7',
                'es_personalizado': False,
            },
            {
                'nombre': 'Peso Muerto',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio completo para espalda, glúteos y piernas. Levanta la barra desde el suelo manteniendo la espalda recta.',
                'duracion_min': 0,
                'dificultad': 5,
                'video_url': 'https://www.youtube.com/watch?v=example8',
                'es_personalizado': False,
            },
            {
                'nombre': 'Flexiones de Brazos',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio para pecho, hombros y tríceps. Mantén el cuerpo recto desde la cabeza hasta los talones.',
                'duracion_min': 0,
                'dificultad': 3,
                'video_url': 'https://www.youtube.com/watch?v=example9',
                'es_personalizado': False,
            },
            {
                'nombre': 'Remo con Barra',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio para espalda y bíceps. Tira de la barra hacia el pecho manteniendo la espalda recta.',
                'duracion_min': 0,
                'dificultad': 3,
                'video_url': 'https://www.youtube.com/watch?v=example10',
                'es_personalizado': False,
            },
            {
                'nombre': 'Press Militar',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio para hombros y tríceps. Empuja la barra desde los hombros hacia arriba.',
                'duracion_min': 0,
                'dificultad': 4,
                'video_url': 'https://www.youtube.com/watch?v=example11',
                'es_personalizado': False,
            },
            {
                'nombre': 'Curl de Bíceps',
                'tipo': 'fuerza',
                'descripcion': 'Ejercicio de aislamiento para bíceps. Levanta las mancuernas flexionando los codos.',
                'duracion_min': 0,
                'dificultad': 2,
                'video_url': 'https://www.youtube.com/watch?v=example12',
                'es_personalizado': False,
            },
            # Movilidad
            {
                'nombre': 'Estiramiento de Cuádriceps',
                'tipo': 'movilidad',
                'descripcion': 'Estira el músculo cuádriceps de la pierna. Agarra el tobillo y tira suavemente hacia los glúteos.',
                'duracion_min': 5,
                'dificultad': 1,
                'video_url': 'https://www.youtube.com/watch?v=example13',
                'es_personalizado': False,
            },
            {
                'nombre': 'Estiramiento de Isquiotibiales',
                'tipo': 'movilidad',
                'descripcion': 'Estira la parte posterior del muslo. Inclínate hacia adelante manteniendo las piernas rectas.',
                'duracion_min': 5,
                'dificultad': 1,
                'video_url': 'https://www.youtube.com/watch?v=example14',
                'es_personalizado': False,
            },
            {
                'nombre': 'Yoga - Saludo al Sol',
                'tipo': 'movilidad',
                'descripcion': 'Secuencia de movimientos de yoga que mejora flexibilidad y movilidad articular.',
                'duracion_min': 10,
                'dificultad': 2,
                'video_url': 'https://www.youtube.com/watch?v=example15',
                'es_personalizado': False,
            },
            {
                'nombre': 'Rotación de Hombros',
                'tipo': 'movilidad',
                'descripcion': 'Movimientos circulares de los hombros para mejorar movilidad y prevenir lesiones.',
                'duracion_min': 3,
                'dificultad': 1,
                'video_url': 'https://www.youtube.com/watch?v=example16',
                'es_personalizado': False,
            },
            {
                'nombre': 'Estiramiento de Espalda',
                'tipo': 'movilidad',
                'descripcion': 'Estira la columna vertebral y músculos de la espalda. Perfecto para después del entrenamiento.',
                'duracion_min': 5,
                'dificultad': 1,
                'video_url': 'https://www.youtube.com/watch?v=example17',
                'es_personalizado': False,
            },
        ]
        
        creados = 0
        actualizados = 0
        
        for ej_data in ejercicios:
            ejercicio, created = Exercise.objects.get_or_create(
                nombre=ej_data['nombre'],
                defaults=ej_data
            )
            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Creado: {ejercicio.nombre}'))
            else:
                # Actualizar si ya existe
                for key, value in ej_data.items():
                    setattr(ejercicio, key, value)
                ejercicio.save()
                actualizados += 1
                self.stdout.write(self.style.WARNING(f'[ACTUALIZADO] Actualizado: {ejercicio.nombre}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] Proceso completado: {creados} creados, {actualizados} actualizados'
        ))
        self.stdout.write(f'Total de ejercicios en BD: {Exercise.objects.count()}')

