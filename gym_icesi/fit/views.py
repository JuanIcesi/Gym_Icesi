# fit/views.py
from datetime import date, timedelta
from calendar import monthrange

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Sum, Max, Avg, Q
from django.db import models as django_models
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Exercise,
    Routine,
    RoutineItem,
    ProgressLog,
    TrainerAssignment,
    UserMonthlyStats,
    TrainerMonthlyStats,
    TrainerRecommendation,
    UserProfile,
    Message,
    EventoInstitucional,
    InscripcionEvento,
    EspacioDeportivo,
    ReservaEspacio,
    AssignmentHistory,
    ContentModeration,
    SystemConfig,
)
from .forms import (
    RoutineForm, RoutineItemForm, ProgressForm, ExerciseForm, TrainerRecommendationForm,
    UserProfileForm, MessageForm, ReservaEspacioForm
)
from fit.institutional_models import InstitutionalUser
from fit.mongodb_service import (
    ProgressLogService,
    ActivityLogService,
    ExerciseDetailsService,
    ExerciseService,
    RoutineService,
    TrainerAssignmentService,
)


# ----------------------------- Página de Inicio / Selección de Login -----------------------------
def index(request):
    """
    Página de inicio donde se puede elegir el tipo de login
    """
    return render(request, "fit/index.html")


# ----------------------------- Aux institucional -----------------------------
def get_institutional_info(username):
    data = {}
    try:
        iu = InstitutionalUser.objects.get(username=username, is_active=True)
        data["role"] = iu.role
        data["student_id"] = iu.student_id
        data["employee_id"] = iu.employee_id

        try:
            with connection.cursor() as cur:
                if iu.student_id:
                    cur.execute(
                        """
                        SELECT s.first_name, s.last_name, s.email, c.name AS campus
                        FROM students s
                        JOIN campuses c ON s.campus_code = c.code
                        WHERE s.id = %s
                        """,
                        [iu.student_id],
                    )
                    row = cur.fetchone()
                    if row:
                        data.update(
                            {
                                "first_name": row[0],
                                "last_name": row[1],
                                "email": row[2],
                                "campus": row[3],
                            }
                        )
                elif iu.employee_id:
                    cur.execute(
                        """
                        SELECT e.first_name, e.last_name, e.email, f.name AS faculty
                        FROM employees e
                        JOIN faculties f ON e.faculty_code = f.code
                        WHERE e.id = %s
                        """,
                        [iu.employee_id],
                    )
                    row = cur.fetchone()
                    if row:
                        data.update(
                            {
                                "first_name": row[0],
                                "last_name": row[1],
                                "email": row[2],
                                "faculty": row[3],
                            }
                        )
        except Exception:
            # Si falla (por ejemplo, usando SQLite sin BD institucional), continuar sin datos adicionales
            pass
    except InstitutionalUser.DoesNotExist:
        pass
    return data


# --------------------------------- Home -------------------------------------
@login_required
def home(request):
    user = request.user
    info = get_institutional_info(user.username)

    # Si es administrador, mostrar estadísticas globales
    if user.is_superuser:
        return admin_dashboard(request)
    
    # Si es entrenador (solo Instructores), mostrar dashboard de entrenador
    # Verificar que realmente sea Instructor, no solo is_staff
    if user.is_staff and not user.is_superuser:
        # Verificar que sea Instructor
        from fit.institutional_models import InstitutionalUser
        try:
            iu = InstitutionalUser.objects.get(username=user.username)
            if iu.role == 'EMPLOYEE' and iu.employee_id:
                with connection.cursor() as cur:
                    cur.execute(
                        "SELECT employee_type FROM employees WHERE id = %s",
                        [iu.employee_id]
                    )
                    row = cur.fetchone()
                    if row and row[0] and row[0].upper() == "INSTRUCTOR":
                        return trainer_dashboard(request)
        except Exception:
            pass
    
    # Dashboard de usuario estándar
    latest = ProgressLog.objects.filter(user=user).order_by("-fecha")[:5]
    my_routines = Routine.objects.filter(user=user).order_by("-fecha_creacion")[:5]

    # Rutinas activas (todas las rutinas del usuario)
    active_routines = Routine.objects.filter(user=user).count()
    
    total_routines = Routine.objects.filter(user=user).count()
    total_sessions = ProgressLog.objects.filter(user=user).count()

    today = date.today()
    current_month_sessions = ProgressLog.objects.filter(
        user=user, fecha__year=today.year, fecha__month=today.month
    )
    monthly_count = current_month_sessions.count()
    active_days = current_month_sessions.values("fecha").distinct().count()
    
    # Tiempo total entrenado este mes (en minutos)
    total_time_minutes = current_month_sessions.aggregate(
        total=Sum("tiempo_seg")
    )["total"] or 0
    total_time_hours = round(total_time_minutes / 60, 1) if total_time_minutes else 0
    
    avg_effort = current_month_sessions.aggregate(avg=Sum("esfuerzo"))["avg"] or 0
    if monthly_count:
        avg_effort = round(avg_effort / monthly_count, 1)
    
    # Entrenador asignado
    trainer_assignment = TrainerAssignment.objects.filter(
        user=user, activo=True
    ).select_related("trainer").first()
    
    trainer_name = None
    if trainer_assignment:
        trainer_info = get_institutional_info(trainer_assignment.trainer.username)
        trainer_name = f"{trainer_info.get('first_name', '')} {trainer_info.get('last_name', '')}".strip()
        if not trainer_name:
            trainer_name = trainer_assignment.trainer.username
    
    # Recomendaciones no leídas
    unread_recommendations = TrainerRecommendation.objects.filter(
        user=user,
        leido=False
    ).count()

    # Verificar si tiene entrenador asignado para el menú
    has_trainer = trainer_assignment is not None
    
    return render(
        request,
        "fit/home.html",
        {
            "info": info,
            "latest": latest,
            "my_routines": my_routines,
            "active_routines": active_routines,
            "total_routines": total_routines,
            "total_sessions": total_sessions,
            "monthly_count": monthly_count,
            "active_days": active_days,
            "total_time_hours": total_time_hours,
            "avg_effort": avg_effort,
            "trainer_name": trainer_name,
            "trainer_assignment": trainer_assignment,
            "has_trainer": has_trainer,
            "unread_recommendations": unread_recommendations,
        },
    )


# ----------------------------- Dashboard de Entrenador -----------------------------
@login_required
@user_passes_test(lambda u: u.is_staff)
def trainer_dashboard(request):
    """Dashboard específico para entrenadores"""
    user = request.user
    info = get_institutional_info(user.username)
    
    # Usuarios asignados
    asignados = TrainerAssignment.objects.filter(
        trainer=user, activo=True
    ).select_related("user").count()
    
    # Rutinas prediseñadas creadas
    rutinas_predisenadas = Routine.objects.filter(
        es_predisenada=True, autor_trainer=user
    ).count()
    
    # Ejercicios creados
    ejercicios_creados = Exercise.objects.filter(creado_por=user).count()
    
    # Recomendaciones dadas este mes
    hoy = date.today()
    recomendaciones_mes = TrainerRecommendation.objects.filter(
        trainer=user,
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).count()
    
    # Últimos usuarios asignados con información adicional
    ultimos_asignados_list = TrainerAssignment.objects.filter(
        trainer=user, activo=True
    ).select_related("user").order_by("-fecha_asignacion")[:5]
    
    # Agregar información de última sesión y nivel de actividad
    ultimos_asignados = []
    for asignado in ultimos_asignados_list:
        ultima_sesion = ProgressLog.objects.filter(
            user=asignado.user
        ).order_by("-fecha").first()
        
        # Sesiones este mes
        sesiones_mes = ProgressLog.objects.filter(
            user=asignado.user,
            fecha__year=hoy.year,
            fecha__month=hoy.month
        ).count()
        
        # Nivel de actividad
        if sesiones_mes >= 10:
            nivel_actividad = "Alto"
        elif sesiones_mes >= 5:
            nivel_actividad = "Medio"
        elif sesiones_mes > 0:
            nivel_actividad = "Bajo"
        else:
            nivel_actividad = "Sin actividad"
        
        ultimos_asignados.append({
            "assignment": asignado,
            "ultima_sesion": ultima_sesion,
            "sesiones_mes": sesiones_mes,
            "nivel_actividad": nivel_actividad,
        })
    
    # Usuarios que necesitan atención (sin actividad en los últimos X días)
    usuarios_necesitan_atencion = []
    asignados_todos = TrainerAssignment.objects.filter(
        trainer=user, activo=True
    ).select_related("user")
    
    for asignado in asignados_todos:
        ultima_sesion = ProgressLog.objects.filter(
            user=asignado.user
        ).order_by("-fecha").first()
        
        if not ultima_sesion or (hoy - ultima_sesion.fecha).days > 7:
            # Sin actividad en los últimos 7 días
            user_info = get_institutional_info(asignado.user.username)
            usuarios_necesitan_atencion.append({
                "user": asignado.user,
                "user_info": user_info,
                "dias_sin_actividad": (hoy - ultima_sesion.fecha).days if ultima_sesion else 999,
                "ultima_sesion": ultima_sesion,
            })
    
    # Ordenar por días sin actividad (más días primero)
    usuarios_necesitan_atencion.sort(key=lambda x: x["dias_sin_actividad"], reverse=True)
    usuarios_necesitan_atencion = usuarios_necesitan_atencion[:5]  # Top 5
    
    # Sesiones registradas por tus usuarios este mes
    # Obtener IDs de usuarios asignados activos
    usuarios_asignados_ids = TrainerAssignment.objects.filter(
        trainer=user, activo=True
    ).values_list('user_id', flat=True)
    
    sesiones_usuarios_mes = ProgressLog.objects.filter(
        user_id__in=usuarios_asignados_ids,
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).count()
    
    # Últimas recomendaciones
    ultimas_recomendaciones = TrainerRecommendation.objects.filter(
        trainer=user
    ).select_related("user").order_by("-fecha")[:5]
    
    return render(
        request,
        "fit/trainer_dashboard.html",
        {
            "info": info,
            "asignados": asignados,
            "rutinas_predisenadas": rutinas_predisenadas,
            "ejercicios_creados": ejercicios_creados,
            "recomendaciones_mes": recomendaciones_mes,
            "sesiones_usuarios_mes": sesiones_usuarios_mes,
            "ultimos_asignados": ultimos_asignados,
            "usuarios_necesitan_atencion": usuarios_necesitan_atencion,
            "ultimas_recomendaciones": ultimas_recomendaciones,
        },
    )


# ----------------------------- Dashboard de Administrador -----------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """
    Panel de administración con estadísticas globales.
    Muestra resumen de usuarios, entrenadores, sesiones y permite gestionar asignaciones.
    """
    user = request.user
    info = get_institutional_info(user.username)
    
    # Estadísticas globales
    total_usuarios = User.objects.filter(is_staff=False, is_superuser=False).count()
    # Contar solo Instructores (entrenadores reales)
    total_entrenadores = 0
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM employees 
                WHERE UPPER(employee_type) = 'INSTRUCTOR'
            """)
            row = cur.fetchone()
            if row:
                total_entrenadores = row[0]
    except Exception:
        pass
    total_rutinas = Routine.objects.count()
    total_sesiones = ProgressLog.objects.count()
    
    # Usuarios activos (con actividad este mes)
    hoy = date.today()
    usuarios_activos = ProgressLog.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).values("user").distinct().count()
    
    # Usuarios con entrenador asignado vs sin asignar
    usuarios_con_entrenador = TrainerAssignment.objects.filter(
        activo=True
    ).values("user").distinct().count()
    usuarios_sin_entrenador = total_usuarios - usuarios_con_entrenador
    
    # Entrenadores con más carga (más asignados)
    entrenadores_carga = TrainerAssignment.objects.filter(
        activo=True
    ).values("trainer__username").annotate(
        total_asignados=Count("id")
    ).order_by("-total_asignados")[:5]
    
    # Agregar información institucional a entrenadores
    entrenadores_carga_info = []
    for trainer_data in entrenadores_carga:
        trainer_username = trainer_data["trainer__username"]
        trainer_info = get_institutional_info(trainer_username)
        entrenadores_carga_info.append({
            "username": trainer_username,
            "name": f"{trainer_info.get('first_name', '')} {trainer_info.get('last_name', '')}".strip() or trainer_username,
            "total_asignados": trainer_data["total_asignados"],
        })
    
    # Usuarios más activos este mes
    usuarios_mas_activos = ProgressLog.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).values("user__username").annotate(
        sesiones=Count("id")
    ).order_by("-sesiones")[:5]
    
    # Agregar información institucional
    usuarios_mas_activos_info = []
    for user_data in usuarios_mas_activos:
        username = user_data["user__username"]
        user_info = get_institutional_info(username)
        usuarios_mas_activos_info.append({
            "username": username,
            "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or username,
            "sesiones": user_data["sesiones"],
        })
    
    # Rutinas más usadas
    rutinas_mas_usadas = ProgressLog.objects.values(
        "routine__nombre"
    ).annotate(
        veces_usada=Count("id")
    ).order_by("-veces_usada")[:5]
    
    # Estadísticas mensuales
    stats_mes_actual = {
        "rutinas_creadas": Routine.objects.filter(
            fecha_creacion__year=hoy.year,
            fecha_creacion__month=hoy.month
        ).count(),
        "sesiones_registradas": ProgressLog.objects.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        ).count(),
        "asignaciones_nuevas": TrainerAssignment.objects.filter(
            fecha_asignacion__year=hoy.year,
            fecha_asignacion__month=hoy.month
        ).count(),
    }
    
    return render(
        request,
        "fit/admin_dashboard.html",
        {
            "info": info,
            "total_usuarios": total_usuarios,
            "total_entrenadores": total_entrenadores,
            "total_rutinas": total_rutinas,
            "total_sesiones": total_sesiones,
            "usuarios_activos": usuarios_activos,
            "usuarios_con_entrenador": usuarios_con_entrenador,
            "usuarios_sin_entrenador": usuarios_sin_entrenador,
            "entrenadores_carga": entrenadores_carga_info,
            "usuarios_mas_activos": usuarios_mas_activos_info,
            "rutinas_mas_usadas": rutinas_mas_usadas,
            "stats_mes_actual": stats_mes_actual,
        },
    )


# ------------------------------- Rutinas ------------------------------------
@login_required
def routine_list(request):
    """
    Lista de rutinas del usuario con información de estado y última sesión.
    Incluye rutinas prediseñadas disponibles para adoptar.
    """
    # Rutinas del usuario con información adicional
    routines = Routine.objects.filter(user=request.user).order_by("-fecha_creacion")
    
    # Agregar información de última sesión y estado
    routines_with_info = []
    for routine in routines:
        # Última vez entrenada
        ultima_sesion = ProgressLog.objects.filter(
            routine=routine
        ).order_by("-fecha").first()
        
        # Estado: activa, pausada
        estado = "activa"
        if ultima_sesion:
            # Si no hay sesión en los últimos 30 días, considerar pausada
            from datetime import timedelta
            if (date.today() - ultima_sesion.fecha).days > 30:
                estado = "pausada"
        
        routines_with_info.append({
            "routine": routine,
            "ultima_sesion": ultima_sesion,
            "estado": estado,
            "total_ejercicios": routine.items.count(),
        })
    
    # Rutinas prediseñadas (disponibles para adoptar)
    presets = Routine.objects.filter(
        es_predisenada=True
    ).select_related("autor_trainer").order_by("nombre")
    
    # Agregar información del entrenador para cada preset
    presets_with_info = []
    for preset in presets:
        trainer_info = None
        if preset.autor_trainer:
            trainer_info = get_institutional_info(preset.autor_trainer.username)
        
        presets_with_info.append({
            "routine": preset,
            "trainer_info": trainer_info,
            "total_ejercicios": preset.items.count(),
        })
    
    return render(
        request,
        "fit/routine_list.html",
        {
            "routines": routines_with_info,
            "presets": presets_with_info,
        },
    )


@login_required
def routine_create(request):
    if request.method == "POST":
        form = RoutineForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.user = request.user
            r.save()

            # Guardar rutina en MongoDB (NoSQL) - Integración Dual
            try:
                trainer_id = r.autor_trainer.username if r.autor_trainer else None
                RoutineService.save_user_routine(
                    routine_id=r.id,
                    user_id=request.user.username,
                    nombre=r.nombre,
                    descripcion=r.descripcion,
                    es_predisenada=r.es_predisenada,
                    trainer_id=trainer_id,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"No se pudo guardar rutina en MongoDB: {e}")

            # Registrar actividad en MongoDB
            try:
                ActivityLogService.log_activity(
                    user_id=request.user.username,
                    action="create_routine",
                    entity_type="routine",
                    entity_id=r.id,
                    metadata={"routine_name": r.nombre, "descripcion": r.descripcion[:50] if r.descripcion else ""},
                    request=request
                )
            except Exception:
                pass

            # Las estadísticas se actualizan automáticamente mediante señales
            messages.success(request, "Rutina creada.")
            return redirect("routine_detail", pk=r.pk)
    else:
        form = RoutineForm()
    return render(request, "fit/routine_form.html", {"form": form})


@login_required
def routine_detail(request, pk):
    r = get_object_or_404(Routine, pk=pk)
    if r.user != request.user and not r.es_predisenada:
        messages.error(request, "No puedes ver esta rutina.")
        return redirect("routine_list")
    items = r.items.select_related("exercise").all()
    return render(
        request,
        "fit/routine_detail.html",
        {"routine": r, "items": items},
    )


@login_required
def routine_add_item(request, pk):
    """
    Agregar un ejercicio a una rutina.
    Soporta dos modos:
    1. Desde formulario completo (GET o POST con form)
    2. Desde modal rápido (POST con exercise_id y routine_id)
    """
    r = get_object_or_404(Routine, pk=pk)
    
    # Permitir agregar items si es el dueño o si es entrenador y es rutina prediseñada
    if r.user != request.user and not (request.user.is_staff and r.es_predisenada and r.autor_trainer == request.user):
        messages.error(request, "No tienes permiso para modificar esta rutina.")
        return redirect("routine_detail", pk=pk)
    
    # Modo modal rápido: POST con exercise_id
    if request.method == "POST" and "exercise_id" in request.POST:
        exercise_id = request.POST.get("exercise_id")
        routine_id = request.POST.get("routine_id", pk)
        
        # Validar que la rutina pertenece al usuario
        routine = get_object_or_404(Routine, pk=routine_id, user=request.user)
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        
        # Obtener el siguiente orden
        max_orden = RoutineItem.objects.filter(routine=routine).aggregate(
            max_orden=Max("orden")
        )["max_orden"] or 0
        
        # Crear el item con valores por defecto
        RoutineItem.objects.create(
            routine=routine,
            exercise=exercise,
            orden=max_orden + 1,
            series=3,  # Valores por defecto
            reps=10,
        )
        
        messages.success(request, f"Ejercicio '{exercise.nombre}' agregado a la rutina '{routine.nombre}'.")
        return redirect("routine_detail", pk=routine_id)
    
    # Modo formulario completo
    if request.method == "POST":
        form = RoutineItemForm(request.POST)
        if form.is_valid():
            it = form.save(commit=False)
            it.routine = r
            # Validación mínima: tiempo o series/reps
            if not it.tiempo_seg and not (it.series and it.reps):
                messages.error(request, "Define tiempo (seg) o series/reps.")
                return render(
                    request,
                    "fit/routine_item_form.html",
                    {"form": form, "routine": r},
                )
            it.save()
            messages.success(request, "Ejercicio agregado a la rutina.")
            return redirect("routine_detail", pk=pk)
    else:
        form = RoutineItemForm()
        # Incluir todos los ejercicios disponibles
        form.fields['exercise'].queryset = Exercise.objects.all().order_by('nombre')
    return render(
        request,
        "fit/routine_item_form.html",
        {"form": form, "routine": r},
    )


@login_required
def routine_adopt(request, pk):
    preset = get_object_or_404(Routine, pk=pk, es_predisenada=True)
    nueva = Routine.objects.create(
        user=request.user, nombre=f"{preset.nombre} (mi copia)"
    )
    for i in preset.items.all():
        RoutineItem.objects.create(
            routine=nueva,
            exercise=i.exercise,
            orden=i.orden,
            series=i.series,
            reps=i.reps,
            tiempo_seg=i.tiempo_seg,
            notas=i.notas,
        )
    messages.success(request, "Rutina adoptada.")
    return redirect("routine_detail", pk=nueva.pk)


# ------------------------------- Progreso -----------------------------------
@login_required
def progress_create(request):
    """
    Crear un registro de progreso.
    Puede venir preseleccionada una rutina desde la URL (?routine=id).
    """
    # Preseleccionar rutina si viene en la URL
    routine_id = request.GET.get("routine")
    initial_data = {}
    if routine_id:
        try:
            routine = Routine.objects.get(pk=routine_id, user=request.user)
            initial_data["routine"] = routine
        except Routine.DoesNotExist:
            pass
    
    if request.method == "POST":
        form = ProgressForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            if p.routine.user != request.user:
                messages.error(request, "Rutina inválida.")
                return redirect("progress_create")
            p.user = request.user
            # Si no viene fecha, usar hoy
            if not p.fecha:
                p.fecha = date.today()
            p.save()
            
            # Guardar progreso detallado en MongoDB (NoSQL)
            try:
                # Obtener el primer ejercicio de la rutina si existe
                first_item = p.routine.items.first()
                exercise_id = first_item.exercise.id if first_item else None
                
                ProgressLogService.save_detailed_progress(
                    user_id=request.user.username,
                    routine_id=p.routine.id,
                    exercise_id=exercise_id,
                    fecha=p.fecha,
                    series=p.repeticiones,  # Usando repeticiones como series si aplica
                    reps=None,  # Se puede agregar campo específico después
                    tiempo_seg=p.tiempo_seg,
                    esfuerzo=p.esfuerzo,
                    notas=p.notas
                )
            except Exception as e:
                # Si MongoDB falla, continuar sin error (no crítico)
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"No se pudo guardar en MongoDB: {e}")
            
            # Registrar actividad en MongoDB
            try:
                ActivityLogService.log_activity(
                    user_id=request.user.username,
                    action="log_progress",
                    entity_type="progress",
                    entity_id=p.id,
                    metadata={
                        "routine_name": p.routine.nombre,
                        "fecha": str(p.fecha),
                        "esfuerzo": p.esfuerzo
                    },
                    request=request
                )
            except Exception:
                pass  # No crítico si falla
            
            # Las estadísticas se actualizan automáticamente mediante señales
            messages.success(request, "Progreso registrado exitosamente.")
            return redirect("progress_list")
    else:
        form = ProgressForm(initial=initial_data)
        form.fields["routine"].queryset = Routine.objects.filter(user=request.user).order_by("nombre")
    return render(request, "fit/progress_form.html", {"form": form, "routine_preselected": routine_id})


@login_required
def progress_list(request):
    """
    Historial de progreso del usuario con filtros por mes, rutina y tipo de ejercicio.
    """
    user = request.user
    progress_logs = ProgressLog.objects.filter(user=user).order_by("-fecha")
    
    # Filtros
    month_filter = request.GET.get("month", "")
    year_filter = request.GET.get("year", "")
    routine_filter = request.GET.get("routine", "")
    
    if month_filter and year_filter:
        try:
            progress_logs = progress_logs.filter(
                fecha__year=int(year_filter),
                fecha__month=int(month_filter)
            )
        except ValueError:
            pass
    
    if routine_filter:
        try:
            progress_logs = progress_logs.filter(routine_id=int(routine_filter))
        except ValueError:
            pass
    
    # Obtener rutinas del usuario para el filtro
    user_routines = Routine.objects.filter(user=user).order_by("nombre")
    
    # Estadísticas del mes actual
    today = date.today()
    current_month_logs = ProgressLog.objects.filter(
        user=user,
        fecha__year=today.year,
        fecha__month=today.month
    )
    total_sessions_month = current_month_logs.count()
    total_time_month = current_month_logs.aggregate(total=Sum("tiempo_seg"))["total"] or 0
    total_time_hours_month = round(total_time_month / 3600, 1) if total_time_month else 0
    
    return render(request, "fit/progress_list.html", {
        "progress_logs": progress_logs,
        "user_routines": user_routines,
        "month_filter": month_filter,
        "year_filter": year_filter,
        "routine_filter": routine_filter,
        "total_sessions_month": total_sessions_month,
        "total_time_hours_month": total_time_hours_month,
    })


# ------------------------- Entrenadores institucionales ----------------------
@login_required
def trainer_detail(request, emp_id: str):
    try:
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT e.id,
                       e.first_name,
                       e.last_name,
                       e.email,
                       e.employee_type,
                       f.name AS faculty,
                       c.name AS campus
                FROM employees e
                JOIN faculties f ON e.faculty_code = f.code
                JOIN campuses c ON e.campus_code = c.code
                WHERE e.id = %s
                """,
                [emp_id],
            )
            row = cur.fetchone()

        if not row:
            messages.error(request, "Entrenador no encontrado.")
            return redirect("trainers")
        
        trainer = {
            "id": row[0],
            "name": f"{row[1]} {row[2]}",
            "email": row[3],
            "type": row[4],
            "faculty": row[5],
            "campus": row[6],
        }

        # Si algún día quieres ver usuarios asignados a ese entrenador
        asignados = (
            TrainerAssignment.objects.filter(trainer__is_staff=True)
            .select_related("user")[:0]
        )

        return render(
            request,
            "fit/trainer_detail.html",
            {"trainer": trainer, "asignados": asignados},
        )
    except Exception:
        messages.error(request, "Error al acceder a la base de datos institucional.")
        return redirect("trainers")


# ------------------------------- Módulo trainer ------------------------------
def is_trainer(u):
    """
    Verifica si un usuario es entrenador.
    Solo los empleados con employee_type = 'Instructor' son entrenadores.
    """
    if not u.is_staff or u.is_superuser:
        return False
    
    # Verificar que realmente sea Instructor en la BD institucional
    from fit.institutional_models import InstitutionalUser
    try:
        iu = InstitutionalUser.objects.get(username=u.username)
        if iu.role == 'EMPLOYEE' and iu.employee_id:
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT employee_type FROM employees WHERE id = %s",
                    [iu.employee_id]
                )
                row = cur.fetchone()
                if row and row[0] and row[0].upper() == "INSTRUCTOR":
                    return True
    except Exception:
        pass
    
    return False


def is_admin(user):
    """
    Solo los usuarios con is_superuser=True son administradores.
    Los entrenadores (is_staff=True pero is_superuser=False) NO son admin.
    """
    return user.is_superuser


@login_required
@user_passes_test(is_trainer)
def trainer_assignees(request):
    """
    Lista de usuarios asignados al entrenador con información de actividad y filtros.
    """
    trainer = request.user
    asignados = TrainerAssignment.objects.filter(
        trainer=trainer, activo=True
    ).select_related("user").order_by("-fecha_asignacion")
    
    # Filtros
    search_query = request.GET.get("q", "")
    actividad_filter = request.GET.get("actividad", "")
    
    if search_query:
        asignados = asignados.filter(
            user__username__icontains=search_query
        )
    
    # Agregar información detallada para cada asignado
    asignados_con_info = []
    for asignado in asignados:
        user = asignado.user
        user_info = get_institutional_info(user.username)
        
        # Última sesión
        ultima_sesion = ProgressLog.objects.filter(
            user=user
        ).order_by("-fecha").first()
        
        # Sesiones este mes
        hoy = date.today()
        sesiones_mes = ProgressLog.objects.filter(
            user=user,
            fecha__year=hoy.year,
            fecha__month=hoy.month
        ).count()
        
        # Nivel de actividad
        if sesiones_mes >= 10:
            nivel_actividad = "Alto"
        elif sesiones_mes >= 5:
            nivel_actividad = "Medio"
        elif sesiones_mes > 0:
            nivel_actividad = "Bajo"
        else:
            nivel_actividad = "Sin actividad"
        
        # Aplicar filtro de actividad
        if actividad_filter:
            if actividad_filter == "alto" and nivel_actividad != "Alto":
                continue
            elif actividad_filter == "medio" and nivel_actividad != "Medio":
                continue
            elif actividad_filter == "bajo" and nivel_actividad not in ["Bajo", "Sin actividad"]:
                continue
        
        # Rutinas activas
        rutinas_activas = Routine.objects.filter(user=user).count()
        
        asignados_con_info.append({
            "assignment": asignado,
            "user_info": user_info,
            "ultima_sesion": ultima_sesion,
            "sesiones_mes": sesiones_mes,
            "nivel_actividad": nivel_actividad,
            "rutinas_activas": rutinas_activas,
        })
    
    return render(
        request,
        "fit/trainer_assignees.html",
        {
            "asignados": asignados_con_info,
            "search_query": search_query,
            "actividad_filter": actividad_filter,
        },
    )


@login_required
@user_passes_test(is_trainer)
def trainer_feedback(request, user_id):
    """
    Vista detalle de usuario para el entrenador.
    Muestra resumen, rutinas activas, progresos recientes y permite enviar recomendaciones.
    """
    tuser = get_object_or_404(User, pk=user_id)
    trainer = request.user
    
    # Verificar asignación
    assignment = TrainerAssignment.objects.filter(
        trainer=trainer,
        user=tuser,
        activo=True
    ).first()
    
    if not assignment:
        messages.error(request, "Este usuario no está asignado a ti.")
        return redirect("trainer_assignees")
    
    # Información institucional del usuario
    user_info = get_institutional_info(tuser.username)
    
    # Progresos recientes
    progress = ProgressLog.objects.filter(user=tuser).order_by("-fecha")[:10]
    
    # Rutinas del usuario
    routines = Routine.objects.filter(user=tuser).order_by("-fecha_creacion")
    
    # Recomendaciones enviadas
    recommendations = TrainerRecommendation.objects.filter(
        trainer=trainer,
        user=tuser
    ).order_by("-fecha")[:10]
    
    # Estadísticas del usuario
    hoy = date.today()
    sesiones_mes = ProgressLog.objects.filter(
        user=tuser,
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).count()
    
    rutinas_activas = routines.count()
    
    # Tendencia de actividad (últimos 3 meses)
    tendencia = []
    for i in range(3):
        mes_fecha = date(hoy.year, hoy.month - i, 1) if hoy.month > i else date(hoy.year - 1, 12 + hoy.month - i, 1)
        sesiones = ProgressLog.objects.filter(
            user=tuser,
            fecha__year=mes_fecha.year,
            fecha__month=mes_fecha.month
        ).count()
        tendencia.append({
            "mes": mes_fecha.strftime("%b %Y"),
            "sesiones": sesiones,
        })
    tendencia.reverse()
    
    return render(
        request,
        "fit/trainer_feedback.html",
        {
            "tuser": tuser,
            "user_info": user_info,
            "progress": progress,
            "routines": routines,
            "recommendations": recommendations,
            "assignment": assignment,
            "sesiones_mes": sesiones_mes,
            "rutinas_activas": rutinas_activas,
            "tendencia": tendencia,
        },
    )


@login_required
@user_passes_test(is_admin)
def trainers_list(request):
    """
    Lista SOLO los entrenadores reales desde EMPLOYEES,
    filtrando por employee_type = 'INSTRUCTOR'.
    """
    trainers = []
    try:
        sql = """
            SELECT e.id,
                   e.first_name,
                   e.last_name,
                   e.email,
                   e.employee_type,
                   e.contract_type
            FROM employees e
            WHERE UPPER(e.employee_type) = 'INSTRUCTOR'
            ORDER BY e.last_name, e.first_name
            LIMIT 200;
        """
        with connection.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        trainers = [
            {
                "id": r[0],
                "first_name": r[1],
                "last_name": r[2],
                "full_name": f"{r[1]} {r[2]}",
                "email": r[3],
                "employee_type": r[4],
                "contract_type": r[5],
            }
            for r in rows
        ]
    except Exception:
        # Si falla (por ejemplo, usando SQLite sin BD institucional), mostrar lista vacía
        pass

    return render(request, "fit/trainers_list.html", {"trainers": trainers})


@login_required
def trainers_view(request):
    """
    Vista para cualquier usuario logueado:
    muestra SOLO los empleados con employee_type = 'Instructor' (entrenadores).
    """
    trainers = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT e.id,
                       e.first_name,
                       e.last_name,
                       e.email,
                       f.name AS faculty,
                       e.employee_type
                FROM employees e
                JOIN faculties f ON e.faculty_code = f.code
                WHERE UPPER(e.employee_type) = 'INSTRUCTOR'
                ORDER BY e.last_name, e.first_name;
            """)
            for (emp_id, fn, ln, email, faculty, emp_type) in cur.fetchall():
                trainers.append({
                    "id": emp_id,
                    "name": f"{fn} {ln}",
                    "email": email,
                    "faculty": faculty,
                    "employee_type": emp_type,
                })
    except Exception as e:
        # Si falla (por ejemplo, usando SQLite sin BD institucional), mostrar lista vacía
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al obtener entrenadores: {e}")
        pass

    return render(request, "fit/trainers.html", {"trainers": trainers})



# ------------------------------- Reportes/Admin ------------------------------
@login_required
def report_adherence(request):
    """
    Informe de adherencia y consistencia.
    Muestra días planificados vs días realmente entrenados, porcentaje de cumplimiento,
    y racha actual de días consecutivos.
    """
    user = request.user
    hoy = date.today()
    
    # Obtener mes/año de los parámetros o usar el actual
    year = int(request.GET.get("year", hoy.year))
    month = int(request.GET.get("month", hoy.month))
    
    try:
        inicio = date(year, month, 1)
        fin = date(year, month, monthrange(year, month)[1])
        dias_del_mes = monthrange(year, month)[1]
    except (ValueError, TypeError):
        inicio = date(hoy.year, hoy.month, 1)
        fin = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])
        dias_del_mes = monthrange(hoy.year, hoy.month)[1]
        year = hoy.year
        month = hoy.month

    logs = ProgressLog.objects.filter(user=user, fecha__range=(inicio, fin))
    dias_activos = logs.values("fecha").distinct().count()
    total_sesiones = logs.count()
    porcentaje_adherencia = round((dias_activos / dias_del_mes) * 100, 1) if dias_del_mes > 0 else 0
    
    # Calcular racha actual (días consecutivos entrenando)
    racha_actual = 0
    fecha_actual = hoy
    while True:
        if ProgressLog.objects.filter(user=user, fecha=fecha_actual).exists():
            racha_actual += 1
            fecha_actual -= timedelta(days=1)
        else:
            break
    
    # Días planificados (asumiendo que las rutinas sugieren ciertos días)
    # Por ahora, calculamos basado en rutinas activas
    rutinas_activas = Routine.objects.filter(user=user).count()
    # Estimación: si tiene rutinas, asumimos que planifica entrenar 3-4 veces por semana
    dias_planificados_estimados = round((dias_del_mes / 7) * 3.5) if rutinas_activas > 0 else 0
    
    por_tipo = (
        logs.values("routine__items__exercise__tipo")
        .annotate(sesiones=Count("id"))
        .order_by()
    )
    
    # Esfuerzo promedio
    esfuerzo_promedio = logs.aggregate(avg=Avg("esfuerzo"))["avg"] or 0
    esfuerzo_promedio = round(esfuerzo_promedio, 1)
    
    # Rutinas más usadas
    rutinas_mas_usadas = (
        logs.values("routine__nombre")
        .annotate(veces=Count("id"))
        .order_by("-veces")[:5]
    )
    
    # Porcentaje de cumplimiento (días entrenados vs planificados)
    porcentaje_cumplimiento = 0
    if dias_planificados_estimados > 0:
        porcentaje_cumplimiento = round((dias_activos / dias_planificados_estimados) * 100, 1)
    
    # Mejor semana del mes
    sesiones_por_semana = {}
    for log in logs:
        semana = (log.fecha.day - 1) // 7 + 1
        sesiones_por_semana[semana] = sesiones_por_semana.get(semana, 0) + 1
    mejor_semana = None
    if sesiones_por_semana:
        mejor_semana = max(sesiones_por_semana.items(), key=lambda x: x[1])

    return render(
        request,
        "fit/report_adherence.html",
        {
            "year": year,
            "month": month,
            "dias_activos": dias_activos,
            "total_sesiones": total_sesiones,
            "dias_del_mes": dias_del_mes,
            "dias_planificados_estimados": dias_planificados_estimados,
            "porcentaje_adherencia": porcentaje_adherencia,
            "porcentaje_cumplimiento": porcentaje_cumplimiento,
            "racha_actual": racha_actual,
            "esfuerzo_promedio": esfuerzo_promedio,
            "por_tipo": por_tipo,
            "rutinas_mas_usadas": rutinas_mas_usadas,
            "mejor_semana": mejor_semana,
            "periodo": (inicio, fin),
        },
    )


@login_required
def report_load_balance(request):
    """Reporte mejorado de balance de carga"""
    agg = (
        ProgressLog.objects.filter(user=request.user)
        .values("routine__items__exercise__tipo")
        .annotate(
            total_reps=Sum("repeticiones"),
            total_tiempo=Sum("tiempo_seg"),
            sesiones=Count("id"),
        )
        .order_by()
    )
    
    # Calcular totales
    total_reps_all = sum(item["total_reps"] or 0 for item in agg)
    total_tiempo_all = sum(item["total_tiempo"] or 0 for item in agg)
    
    # Evolución semanal (últimas 4 semanas)
    hoy = date.today()
    semanas = []
    for i in range(4):
        semana_inicio = hoy - timedelta(days=hoy.weekday() + (i * 7))
        semana_fin = semana_inicio + timedelta(days=6)
        sesiones_semana = ProgressLog.objects.filter(
            user=request.user,
            fecha__range=(semana_inicio, semana_fin)
        ).count()
        semanas.append({
            "inicio": semana_inicio,
            "fin": semana_fin,
            "sesiones": sesiones_semana,
        })
    
    return render(request, "fit/report_load_balance.html", {
        "agg": agg,
        "total_reps_all": total_reps_all,
        "total_tiempo_all": total_tiempo_all,
        "semanas": reversed(semanas),
    })


@login_required
def report_progress(request):
    """
    Informe de progreso mensual con gráficas y estadísticas detalladas.
    Permite seleccionar mes/año.
    """
    user = request.user
    
    # Obtener mes/año de los parámetros o usar el actual
    hoy = date.today()
    year = int(request.GET.get("year", hoy.year))
    month = int(request.GET.get("month", hoy.month))
    
    try:
        inicio = date(year, month, 1)
        fin = date(year, month, monthrange(year, month)[1])
    except (ValueError, TypeError):
        inicio = date(hoy.year, hoy.month, 1)
        fin = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])
        year = hoy.year
        month = hoy.month
    
    # Logs del mes seleccionado
    logs = ProgressLog.objects.filter(user=user, fecha__range=(inicio, fin))
    
    # Estadísticas básicas
    total_sesiones = logs.count()
    dias_activos = logs.values("fecha").distinct().count()
    total_tiempo_seg = logs.aggregate(total=Sum("tiempo_seg"))["total"] or 0
    total_tiempo_horas = round(total_tiempo_seg / 3600, 1) if total_tiempo_seg else 0
    
    # Rutinas diferentes usadas
    rutinas_usadas = logs.values("routine__nombre").distinct().count()
    
    # Esfuerzo promedio
    esfuerzo_promedio = logs.aggregate(avg=Avg("esfuerzo"))["avg"] or 0
    esfuerzo_promedio = round(esfuerzo_promedio, 1)
    
    # Sesiones por semana del mes (para gráfica de barras)
    sesiones_por_semana = {}
    for log in logs:
        semana = (log.fecha.day - 1) // 7 + 1
        sesiones_por_semana[semana] = sesiones_por_semana.get(semana, 0) + 1
    
    # Distribución por tipo de ejercicio (para gráfica de pastel)
    distribucion_tipo = {}
    for log in logs:
        tipos = log.routine.items.values_list("exercise__tipo", flat=True).distinct()
        for tipo in tipos:
            if tipo:
                distribucion_tipo[tipo] = distribucion_tipo.get(tipo, 0) + 1
    
    # Hitos del mes
    hitos = []
    if total_sesiones > 0:
        hitos.append(f"Primera sesión del mes: {logs.order_by('fecha').first().fecha.strftime('%d de %B')}")
    if total_sesiones >= 10:
        hitos.append(f"¡10+ sesiones completadas este mes!")
    if dias_activos >= 15:
        hitos.append(f"¡15+ días activos este mes!")
    if esfuerzo_promedio >= 8:
        hitos.append(f"¡Esfuerzo promedio alto ({esfuerzo_promedio}/10)!")
    
    # Semana con más sesiones
    if sesiones_por_semana:
        semana_max = max(sesiones_por_semana.items(), key=lambda x: x[1])
        hitos.append(f"Mejor semana: Semana {semana_max[0]} con {semana_max[1]} sesiones")
    
    return render(request, "fit/report_progress.html", {
        "year": year,
        "month": month,
        "inicio": inicio,
        "fin": fin,
        "total_sesiones": total_sesiones,
        "dias_activos": dias_activos,
        "total_tiempo_horas": total_tiempo_horas,
        "rutinas_usadas": rutinas_usadas,
        "esfuerzo_promedio": esfuerzo_promedio,
        "sesiones_por_semana": sesiones_por_semana,
        "distribucion_tipo": distribucion_tipo,
        "hitos": hitos,
    })


@login_required
def report_progress_trend(request):
    """Nuevo informe: Tendencias de progreso"""
    # Progreso de los últimos 3 meses
    hoy = date.today()
    meses_datos = []
    
    for i in range(3):
        mes_fecha = date(hoy.year, hoy.month - i, 1) if hoy.month > i else date(hoy.year - 1, 12 + hoy.month - i, 1)
        anio_mes = mes_fecha.year
        mes_num = mes_fecha.month
        
        logs_mes = ProgressLog.objects.filter(
            user=request.user,
            fecha__year=anio_mes,
            fecha__month=mes_num
        )
        
        esfuerzo_avg = logs_mes.aggregate(avg=Avg("esfuerzo"))["avg"] or 0
        
        meses_datos.append({
            "mes": mes_fecha.strftime("%B %Y"),
            "sesiones": logs_mes.count(),
            "esfuerzo_promedio": round(esfuerzo_avg, 1) if logs_mes.count() > 0 else 0,
            "rutinas_activas": logs_mes.values("routine").distinct().count(),
        })
    
    return render(request, "fit/report_progress_trend.html", {
        "meses_datos": reversed(meses_datos),
    })


@login_required
def report_achievements(request):
    """Nuevo informe: Logros y metas"""
    total_rutinas = Routine.objects.filter(user=request.user).count()
    total_sesiones = ProgressLog.objects.filter(user=request.user).count()
    dias_consecutivos = 0
    
    # Calcular días consecutivos (desde hoy hacia atrás)
    hoy = date.today()
    dias_consecutivos = 0
    fecha_actual = hoy
    
    # Verificar si hay actividad hoy
    if ProgressLog.objects.filter(user=request.user, fecha=hoy).exists():
        dias_consecutivos = 1
        fecha_actual = hoy - timedelta(days=1)
        
        # Continuar contando hacia atrás
        while True:
            if ProgressLog.objects.filter(user=request.user, fecha=fecha_actual).exists():
                dias_consecutivos += 1
                fecha_actual = fecha_actual - timedelta(days=1)
            else:
                break
    
    # Rutina más usada
    rutina_mas_usada = (
        ProgressLog.objects.filter(user=request.user)
        .values("routine__nombre")
        .annotate(veces=Count("id"))
        .order_by("-veces")
        .first()
    )
    
    # Mejor esfuerzo
    mejor_esfuerzo = ProgressLog.objects.filter(user=request.user).aggregate(max_effort=Max("esfuerzo"))["max_effort"] or 0
    
    return render(request, "fit/report_achievements.html", {
        "total_rutinas": total_rutinas,
        "total_sesiones": total_sesiones,
        "dias_consecutivos": dias_consecutivos,
        "rutina_mas_usada": rutina_mas_usada,
        "mejor_esfuerzo": mejor_esfuerzo,
    })


@login_required
@user_passes_test(is_admin)
def admin_assign_trainer(request):
    """
    Vista para asignar entrenadores a usuarios.
    Permite buscar usuarios y entrenadores, ver asignaciones actuales y crear/modificar asignaciones.
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        trainer_id = request.POST.get("trainer_id")
        action = request.POST.get("action", "assign")  # assign o deactivate
        
        if action == "deactivate":
            # Desactivar asignación
            assignment_id = request.POST.get("assignment_id")
            assignment = get_object_or_404(TrainerAssignment, pk=assignment_id)
            assignment.activo = False
            assignment.save()
            messages.success(request, f"Asignación desactivada para {assignment.user.username}.")
            return redirect("admin_assign_trainer")
        
        # Crear o actualizar asignación
        user = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
        # El entrenador puede ser cualquier empleado de la BD institucional
        trainer = get_object_or_404(User, pk=trainer_id)

        # Desactivar asignaciones anteriores del usuario
        TrainerAssignment.objects.filter(user=user, activo=True).update(activo=False)

        # Crear nueva asignación
        assignment, created = TrainerAssignment.objects.get_or_create(
            user=user,
            trainer=trainer,
            defaults={"activo": True}
        )
        
        if not created:
            assignment.activo = True
            assignment.save()

        # Guardar asignación en MongoDB (NoSQL) - Integración Dual
        try:
            TrainerAssignmentService.save_assignment(
                assignment_id=assignment.id,
                user_id=user.username,
                trainer_id=trainer.username,
                fecha_asignacion=assignment.fecha_asignacion,
                activo=assignment.activo,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No se pudo guardar asignación en MongoDB: {e}")

        # Registrar actividad en MongoDB
        try:
            ActivityLogService.log_activity(
                user_id=request.user.username,
                action="assign_trainer",
                entity_type="trainer_assignment",
                entity_id=assignment.id,
                metadata={
                    "user": user.username,
                    "trainer": trainer.username,
                    "created": created
                },
                request=request
            )
        except Exception:
            pass

        messages.success(request, f"Entrenador asignado exitosamente a {user.username}.")
        return redirect("admin_assign_trainer")

    # Búsqueda de usuarios
    search_user = request.GET.get("search_user", "")
    search_trainer = request.GET.get("search_trainer", "")
    
    # Obtener usuarios directamente de la BD institucional
    # Incluir: Estudiantes (STUDENT) y Empleados que NO sean Instructores ni Administrativos (Docentes)
    users_from_db = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT u.username, u.role, u.student_id, u.employee_id
                FROM users u
                WHERE u.is_active = TRUE
                AND u.username NOT LIKE 'test%'
                AND (
                    u.role = 'STUDENT'
                    OR (
                        u.role = 'EMPLOYEE' 
                        AND u.employee_id IS NOT NULL
                        AND EXISTS (
                            SELECT 1 FROM employees e 
                            WHERE e.id = u.employee_id 
                            AND UPPER(e.employee_type) NOT IN ('INSTRUCTOR', 'ADMINISTRATIVO')
                        )
                    )
                )
                ORDER BY u.username
            """)
            for row in cur.fetchall():
                username, role, student_id, employee_id = row
                
                # Filtrar usuarios de prueba
                if 'test' in username.lower():
                    continue
                
                # Aplicar búsqueda si existe
                if search_user and search_user.lower() not in username.lower():
                    continue
                
                # Obtener o crear usuario Django si no existe
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_staff': False, 'is_superuser': False}
                )
                
                # Asegurar que no sea staff ni superuser (son usuarios estándar)
                if not created:
                    if user.is_staff or user.is_superuser:
                        # Verificar si realmente debería ser usuario estándar
                        # (por si cambió su rol en la BD institucional)
                        user.is_staff = False
                        user.is_superuser = False
                        user.save()
                
                # Obtener información institucional
                user_info = get_institutional_info(username)
                
                # Obtener asignación actual
                current_assignment = TrainerAssignment.objects.filter(
                    user=user, activo=True
                ).select_related("trainer").first()
                
                users_from_db.append({
                    "user": user,
                    "user_info": user_info,
                    "current_assignment": current_assignment,
                })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al obtener usuarios de BD institucional: {e}")
        # Fallback: usar solo los que existen en Django
        users_query = User.objects.filter(is_staff=False, is_superuser=False)
        if search_user:
            users_query = users_query.filter(username__icontains=search_user)
        users = users_query.order_by("username")[:50]
        
        users_from_db = []
        for user in users:
            user_info = get_institutional_info(user.username)
            current_assignment = TrainerAssignment.objects.filter(
                user=user, activo=True
            ).select_related("trainer").first()
            
            users_from_db.append({
                "user": user,
                "user_info": user_info,
                "current_assignment": current_assignment,
            })
    
    users_with_info = users_from_db
    
    # Obtener entrenadores directamente de la BD institucional
    # Solo empleados con employee_type = 'Instructor' pueden ser entrenadores
    trainers_from_db = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT u.username, u.employee_id, e.first_name, e.last_name, e.employee_type
                FROM users u
                JOIN employees e ON u.employee_id = e.id
                WHERE u.role = 'EMPLOYEE'
                AND UPPER(e.employee_type) = 'INSTRUCTOR'
                AND u.username NOT LIKE 'test%'
                ORDER BY e.last_name, e.first_name
            """)
            for row in cur.fetchall():
                username, emp_id, first_name, last_name, emp_type = row
                # Filtrar usuarios de prueba
                if 'test' in username.lower():
                    continue
                if search_trainer and search_trainer.lower() not in username.lower():
                    continue
                
                # Obtener o crear usuario Django si no existe
                trainer_user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_staff': True, 'is_superuser': False}
                )
                
                # Si el usuario ya existía pero no tenía is_staff, actualizarlo
                if not created and not trainer_user.is_staff:
                    trainer_user.is_staff = True
                    trainer_user.save()
                
                trainer_info = get_institutional_info(username)
                # Contar usuarios asignados
                asignados_count = TrainerAssignment.objects.filter(
                    trainer=trainer_user, activo=True
                ).count()
                
                trainers_from_db.append({
                    "trainer": trainer_user,
                    "trainer_info": trainer_info,
                    "asignados_count": asignados_count,
                })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al obtener entrenadores de BD institucional: {e}")
        # Fallback: usar solo los que tienen is_staff=True
        trainers_query = User.objects.filter(is_staff=True, is_superuser=False)
        if search_trainer:
            trainers_query = trainers_query.filter(username__icontains=search_trainer)
        trainers = trainers_query.order_by("username")
        
        trainers_with_info = []
        for trainer in trainers:
            trainer_info = get_institutional_info(trainer.username)
            asignados_count = TrainerAssignment.objects.filter(
                trainer=trainer, activo=True
            ).count()
            
            trainers_with_info.append({
                "trainer": trainer,
                "trainer_info": trainer_info,
                "asignados_count": asignados_count,
            })
        trainers_from_db = trainers_with_info
    
    trainers_with_info = trainers_from_db

    return render(
        request,
        "fit/admin_assign_trainer.html",
        {
            "users": users_with_info,
            "trainers": trainers_with_info,
            "search_user": search_user,
            "search_trainer": search_trainer,
        },
    )


@login_required
@user_passes_test(is_admin)
def recalc_stats_month(request):
    hoy = date.today()
    anio, mes = hoy.year, hoy.month

    ui, _ = UserMonthlyStats.objects.get_or_create(
        user=request.user,
        anio=anio,
        mes=mes,
    )
    ui.seguimientos_registrados = ProgressLog.objects.filter(
        user=request.user, fecha__year=anio, fecha__month=mes
    ).count()
    ui.rutinas_iniciadas = Routine.objects.filter(
        user=request.user,
        fecha_creacion__year=anio,
        fecha_creacion__month=mes,
    ).count()
    ui.save()

    messages.success(request, "Stats actualizadas para tu usuario.")
    return redirect("home")


# ==================== NUEVAS FUNCIONALIDADES ====================

# ------------------------- Actualización automática de estadísticas --------------------------
def update_user_stats(user, anio, mes):
    """Actualiza las estadísticas mensuales de un usuario"""
    stats, _ = UserMonthlyStats.objects.get_or_create(
        user=user,
        anio=anio,
        mes=mes,
    )
    stats.rutinas_iniciadas = Routine.objects.filter(
        user=user,
        fecha_creacion__year=anio,
        fecha_creacion__month=mes,
    ).count()
    stats.seguimientos_registrados = ProgressLog.objects.filter(
        user=user,
        fecha__year=anio,
        fecha__month=mes,
    ).count()
    stats.save()
    return stats


def update_trainer_stats(trainer, anio, mes):
    """Actualiza las estadísticas mensuales de un entrenador"""
    stats, _ = TrainerMonthlyStats.objects.get_or_create(
        trainer=trainer,
        anio=anio,
        mes=mes,
    )
    stats.asignaciones_nuevas = TrainerAssignment.objects.filter(
        trainer=trainer,
        fecha_asignacion__year=anio,
        fecha_asignacion__month=mes,
    ).count()
    stats.seguimientos_realizados = TrainerRecommendation.objects.filter(
        trainer=trainer,
        fecha__year=anio,
        fecha__month=mes,
    ).count()
    stats.save()
    return stats


# ------------------------- Ejercicios --------------------------
@login_required
def exercise_create(request):
    """Permite a usuarios crear ejercicios personalizados"""
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.creado_por = request.user
            exercise.es_personalizado = True
            exercise.save()

            # Guardar ejercicio en MongoDB (NoSQL) - Integración Dual
            try:
                ExerciseService.save_exercise(
                    exercise_id=exercise.id,
                    user_id=request.user.username,
                    nombre=exercise.nombre,
                    tipo=exercise.tipo,
                    descripcion=exercise.descripcion,
                    duracion_min=exercise.duracion_min,
                    dificultad=exercise.dificultad,
                    video_url=exercise.video_url,
                    es_personalizado=exercise.es_personalizado,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"No se pudo guardar ejercicio en MongoDB: {e}")

            # Guardar detalles extendidos en MongoDB
            try:
                ExerciseDetailsService.save_exercise_details(
                    exercise_id=exercise.id,
                    tags=[exercise.tipo],
                    nivel_recomendado="intermedio" if exercise.dificultad >= 3 else "principiante"
                )
            except Exception:
                pass

            # Registrar actividad en MongoDB
            try:
                ActivityLogService.log_activity(
                    user_id=request.user.username,
                    action="create_exercise",
                    entity_type="exercise",
                    entity_id=exercise.id,
                    metadata={"exercise_name": exercise.nombre, "tipo": exercise.tipo},
                    request=request
                )
            except Exception:
                pass

            messages.success(request, "Ejercicio creado exitosamente.")
            return redirect("routine_list")
    else:
        form = ExerciseForm()
    return render(request, "fit/exercise_form.html", {"form": form, "title": "Crear Ejercicio Personalizado"})


@login_required
@user_passes_test(is_trainer)
def trainer_exercise_create(request):
    """Permite a entrenadores crear ejercicios para el sistema"""
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.creado_por = request.user
            exercise.es_personalizado = True
            exercise.save()
            messages.success(request, "Ejercicio registrado en el sistema.")
            return redirect("trainer_exercises")
    else:
        form = ExerciseForm()
    return render(request, "fit/exercise_form.html", {"form": form, "title": "Registrar Nuevo Ejercicio"})


@login_required
@user_passes_test(is_trainer)
def trainer_exercises(request):
    """Lista de ejercicios disponibles para entrenadores"""
    exercises = Exercise.objects.all().order_by("nombre")
    return render(request, "fit/trainer_exercises.html", {"exercises": exercises})


# ------------------------- Consulta de Ejercicios (Usuarios) --------------------------
@login_required
def exercises_list(request):
    """
    Lista de ejercicios disponibles para usuarios con búsqueda y filtros avanzados.
    Muestra ejercicios institucionales y creados por entrenadores.
    """
    exercises = Exercise.objects.all().order_by("nombre")
    
    # Búsqueda por nombre
    search_query = request.GET.get("q", "")
    if search_query:
        exercises = exercises.filter(nombre__icontains=search_query)
    
    # Filtro por tipo
    tipo_filter = request.GET.get("tipo", "")
    if tipo_filter:
        exercises = exercises.filter(tipo=tipo_filter)
    
    # Filtro por dificultad
    dificultad_filter = request.GET.get("dificultad", "")
    if dificultad_filter:
        try:
            dificultad_value = int(dificultad_filter)
            exercises = exercises.filter(dificultad=dificultad_value)
        except ValueError:
            pass
    
    # Obtener rutinas del usuario para el modal de agregar a rutina
    user_routines = []
    if request.user.is_authenticated:
        user_routines = Routine.objects.filter(
            user=request.user
        ).order_by("nombre")
    
    return render(request, "fit/exercises_list.html", {
        "exercises": exercises,
        "search_query": search_query,
        "tipo_filter": tipo_filter,
        "dificultad_filter": dificultad_filter,
        "user_routines": user_routines,
    })


@login_required
def exercise_detail(request, pk):
    """
    Detalle completo de un ejercicio con información extendida de MongoDB.
    Incluye modal para agregar el ejercicio a una rutina existente.
    """
    exercise = get_object_or_404(Exercise, pk=pk)
    
    # Obtener detalles extendidos de MongoDB si están disponibles
    mongo_details = None
    try:
        from fit.mongodb_service import ExerciseDetailsService
        mongo_details = ExerciseDetailsService.get_exercise_details(exercise.id)
    except Exception:
        pass
    
    # Obtener rutinas del usuario para el modal
    user_routines = Routine.objects.filter(
        user=request.user
    ).order_by("nombre")
    
    return render(request, "fit/exercise_detail.html", {
        "exercise": exercise,
        "mongo_details": mongo_details,
        "user_routines": user_routines,
    })


# ------------------------- Rutinas Prediseñadas --------------------------
@login_required
@user_passes_test(is_trainer)
def trainer_routine_create(request):
    """Permite a entrenadores crear rutinas prediseñadas"""
    if request.method == "POST":
        form = RoutineForm(request.POST)
        if form.is_valid():
            routine = form.save(commit=False)
            # Las rutinas prediseñadas necesitan un usuario "sistema" o el mismo entrenador
            # Usamos el entrenador como owner pero marcamos como prediseñada
            routine.user = request.user
            routine.es_predisenada = True
            routine.autor_trainer = request.user
            routine.save()

            # Guardar plantilla de rutina en MongoDB (NoSQL) - Integración Dual
            try:
                RoutineService.save_routine_template(
                    routine_id=routine.id,
                    trainer_id=request.user.username,
                    nombre=routine.nombre,
                    descripcion=routine.descripcion,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"No se pudo guardar plantilla en MongoDB: {e}")

            # Registrar actividad en MongoDB
            try:
                ActivityLogService.log_activity(
                    user_id=request.user.username,
                    action="create_preset_routine",
                    entity_type="routine",
                    entity_id=routine.id,
                    metadata={"routine_name": routine.nombre, "is_preset": True},
                    request=request
                )
            except Exception:
                pass

            messages.success(request, "Rutina prediseñada creada. Ahora agrega ejercicios.")
            return redirect("routine_detail", pk=routine.pk)
    else:
        form = RoutineForm()
    return render(request, "fit/routine_form.html", {"form": form, "is_predesigned": True})


@login_required
@user_passes_test(is_trainer)
def trainer_routines(request):
    """Lista de rutinas prediseñadas creadas por el entrenador"""
    routines = Routine.objects.filter(
        es_predisenada=True,
        autor_trainer=request.user
    ).order_by("-fecha_creacion")
    return render(request, "fit/trainer_routines.html", {"routines": routines})


# ------------------------- Recomendaciones --------------------------
@login_required
@user_passes_test(is_trainer)
def trainer_recommendation_create(request, user_id):
    """Permite a entrenadores crear recomendaciones para usuarios asignados"""
    tuser = get_object_or_404(User, pk=user_id)
    
    # Verificar que el usuario esté asignado al entrenador
    assignment = TrainerAssignment.objects.filter(
        trainer=request.user,
        user=tuser,
        activo=True
    ).first()
    
    if not assignment:
        messages.error(request, "Este usuario no está asignado a ti.")
        return redirect("trainer_assignees")
    
    routine_id = request.GET.get("routine_id")
    progress_id = request.GET.get("progress_id")
    
    if request.method == "POST":
        form = TrainerRecommendationForm(request.POST)
        if form.is_valid():
            recommendation = form.save(commit=False)
            recommendation.trainer = request.user
            recommendation.user = tuser
            if routine_id:
                recommendation.routine = get_object_or_404(Routine, pk=routine_id)
            if progress_id:
                recommendation.progress_log = get_object_or_404(ProgressLog, pk=progress_id)
            recommendation.save()
            messages.success(request, "Recomendación enviada.")
            return redirect("trainer_feedback", user_id=user_id)
    else:
        form = TrainerRecommendationForm()
    
    routine = None
    progress = None
    if routine_id:
        routine = get_object_or_404(Routine, pk=routine_id)
    if progress_id:
        progress = get_object_or_404(ProgressLog, pk=progress_id)
    
    return render(request, "fit/trainer_recommendation_form.html", {
        "form": form,
        "tuser": tuser,
        "routine": routine,
        "progress": progress,
    })


@login_required
def recommendations_list(request):
    """Lista de recomendaciones recibidas por el usuario"""
    recommendations = TrainerRecommendation.objects.filter(
        user=request.user
    ).select_related("trainer", "routine", "progress_log").order_by("-fecha")
    
    # Marcar como leídas
    TrainerRecommendation.objects.filter(user=request.user, leido=False).update(leido=True)
    
    return render(request, "fit/recommendations_list.html", {"recommendations": recommendations})

# Las señales para actualización automática de estadísticas están en fit/signals.py
# y se cargan automáticamente desde apps.py cuando Django inicia la aplicación

# ==================== NUEVAS FUNCIONALIDADES ====================

# ------------------------- Perfil de Salud -------------------------
@login_required
def profile_health(request):
    """Vista para configurar/actualizar perfil de salud"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil de salud actualizado correctamente.")
            return redirect("home")
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, "fit/profile_health.html", {"form": form, "profile": profile})

# ------------------------- Mensajería -------------------------
@login_required
def messages_list(request):
    """Lista de mensajes recibidos y enviados"""
    received = Message.objects.filter(destinatario=request.user).order_by("-fecha")
    sent = Message.objects.filter(remitente=request.user).order_by("-fecha")
    unread_count = received.filter(leido=False).count()
    
    return render(request, "fit/messages_list.html", {
        "received": received,
        "sent": sent,
        "unread_count": unread_count,
    })

@login_required
def message_create(request):
    """Crear nuevo mensaje"""
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.remitente = request.user
            msg.save()
            messages.success(request, "Mensaje enviado correctamente.")
            return redirect("messages_list")
    else:
        form = MessageForm()
        # Filtrar destinatarios: solo entrenadores asignados o el entrenador del usuario
        if not request.user.is_staff:
            # Usuario estándar: solo puede enviar a su entrenador
            trainer_assignment = TrainerAssignment.objects.filter(
                user=request.user, activo=True
            ).select_related("trainer").first()
            if trainer_assignment:
                form.fields['destinatario'].queryset = User.objects.filter(
                    id=trainer_assignment.trainer.id
                )
            else:
                form.fields['destinatario'].queryset = User.objects.none()
        else:
            # Entrenador: puede enviar a sus usuarios asignados
            assigned_users = TrainerAssignment.objects.filter(
                trainer=request.user, activo=True
            ).values_list('user_id', flat=True)
            form.fields['destinatario'].queryset = User.objects.filter(id__in=assigned_users)
    
    return render(request, "fit/message_form.html", {"form": form})

@login_required
def message_detail(request, pk):
    """Detalle de un mensaje"""
    message = get_object_or_404(Message, pk=pk)
    
    # Solo el remitente o destinatario pueden ver el mensaje
    if message.remitente != request.user and message.destinatario != request.user:
        messages.error(request, "No tienes permiso para ver este mensaje.")
        return redirect("messages_list")
    
    # Marcar como leído si el usuario es el destinatario
    if message.destinatario == request.user and not message.leido:
        message.leido = True
        message.save()
    
    return render(request, "fit/message_detail.html", {"message": message})

# ------------------------- Calendario y Eventos -------------------------
@login_required
def eventos_list(request):
    """Lista de eventos y talleres institucionales"""
    hoy = date.today()
    eventos_proximos = EventoInstitucional.objects.filter(
        activo=True, fecha_inicio__gte=hoy
    ).order_by("fecha_inicio")
    
    eventos_pasados = EventoInstitucional.objects.filter(
        activo=True, fecha_fin__lt=hoy
    ).order_by("-fecha_inicio")[:10]
    
    # Eventos en los que el usuario está inscrito
    inscripciones = InscripcionEvento.objects.filter(usuario=request.user).values_list('evento_id', flat=True)
    
    return render(request, "fit/eventos_list.html", {
        "eventos_proximos": eventos_proximos,
        "eventos_pasados": eventos_pasados,
        "inscripciones": inscripciones,
    })

@login_required
def evento_detail(request, pk):
    """Detalle de un evento"""
    evento = get_object_or_404(EventoInstitucional, pk=pk, activo=True)
    inscrito = InscripcionEvento.objects.filter(usuario=request.user, evento=evento).exists()
    inscripciones_count = evento.inscripciones.count()
    
    return render(request, "fit/evento_detail.html", {
        "evento": evento,
        "inscrito": inscrito,
        "inscripciones_count": inscripciones_count,
    })

@login_required
def evento_inscribir(request, pk):
    """Inscribirse a un evento"""
    evento = get_object_or_404(EventoInstitucional, pk=pk, activo=True)
    
    # Verificar capacidad
    if evento.capacidad_maxima:
        inscripciones_count = evento.inscripciones.count()
        if inscripciones_count >= evento.capacidad_maxima:
            messages.error(request, "Este evento ya alcanzó su capacidad máxima.")
            return redirect("evento_detail", pk=pk)
    
    # Crear inscripción
    inscripcion, created = InscripcionEvento.objects.get_or_create(
        usuario=request.user,
        evento=evento
    )
    
    if created:
        messages.success(request, f"Te has inscrito al evento: {evento.titulo}")
    else:
        messages.info(request, "Ya estabas inscrito a este evento.")
    
    return redirect("evento_detail", pk=pk)

@login_required
def evento_desinscribir(request, pk):
    """Desinscribirse de un evento"""
    evento = get_object_or_404(EventoInstitucional, pk=pk)
    InscripcionEvento.objects.filter(usuario=request.user, evento=evento).delete()
    messages.success(request, f"Te has desinscrito del evento: {evento.titulo}")
    return redirect("evento_detail", pk=pk)

# ------------------------- Espacios y Reservas -------------------------
@login_required
def espacios_list(request):
    """Lista de espacios deportivos disponibles"""
    espacios = EspacioDeportivo.objects.filter(activo=True).order_by("nombre")
    return render(request, "fit/espacios_list.html", {"espacios": espacios})

@login_required
def espacio_detail(request, pk):
    """Detalle de un espacio deportivo"""
    espacio = get_object_or_404(EspacioDeportivo, pk=pk, activo=True)
    reservas = ReservaEspacio.objects.filter(
        espacio=espacio,
        fecha_reserva__gte=date.today()
    ).order_by("fecha_reserva", "hora_inicio")
    
    return render(request, "fit/espacio_detail.html", {
        "espacio": espacio,
        "reservas": reservas,
    })

@login_required
def reserva_create(request, espacio_id=None):
    """Crear una reserva de espacio"""
    espacio = None
    if espacio_id:
        espacio = get_object_or_404(EspacioDeportivo, pk=espacio_id, activo=True)
    
    if request.method == "POST":
        form = ReservaEspacioForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            
            # Verificar conflictos de horario
            conflictos = ReservaEspacio.objects.filter(
                espacio=reserva.espacio,
                fecha_reserva=reserva.fecha_reserva,
                estado__in=['pendiente', 'confirmada'],
            ).exclude(
                hora_fin__lte=reserva.hora_inicio
            ).exclude(
                hora_inicio__gte=reserva.hora_fin
            )
            
            if conflictos.exists():
                messages.error(request, "Este espacio ya está reservado en ese horario.")
            else:
                reserva.save()
                messages.success(request, "Reserva creada correctamente.")
                return redirect("reservas_list")
    else:
        form = ReservaEspacioForm()
        if espacio:
            form.fields['espacio'].initial = espacio
    
    return render(request, "fit/reserva_form.html", {"form": form, "espacio": espacio})

@login_required
def reservas_list(request):
    """Lista de reservas del usuario"""
    reservas = ReservaEspacio.objects.filter(
        usuario=request.user
    ).order_by("-fecha_reserva", "-hora_inicio")
    
    return render(request, "fit/reservas_list.html", {"reservas": reservas})

@login_required
def reserva_cancel(request, pk):
    """Cancelar una reserva"""
    reserva = get_object_or_404(ReservaEspacio, pk=pk, usuario=request.user)
    reserva.estado = 'cancelada'
    reserva.save()
    messages.success(request, "Reserva cancelada correctamente.")
    return redirect("reservas_list")

# ------------------------- Recordatorios de Rutinas -------------------------
@login_required
def routine_reminders(request):
    """Recordatorios de rutinas pendientes"""
    hoy = date.today()
    rutinas = Routine.objects.filter(user=request.user)
    
    recordatorios = []
    for rutina in rutinas:
        # Obtener última vez que se entrenó esta rutina
        ultimo_progreso = ProgressLog.objects.filter(
            routine=rutina, user=request.user
        ).order_by("-fecha").first()
        
        dias_sin_entrenar = None
        if ultimo_progreso:
            dias_sin_entrenar = (hoy - ultimo_progreso.fecha).days
        else:
            # Nunca se ha entrenado
            dias_sin_entrenar = (hoy - rutina.fecha_creacion.date()).days
        
        # Verificar frecuencia
        necesita_recordatorio = False
        if rutina.frecuencia == 'diaria' and dias_sin_entrenar >= 1:
            necesita_recordatorio = True
        elif rutina.frecuencia == 'semanal' and dias_sin_entrenar >= 7:
            necesita_recordatorio = True
        elif rutina.frecuencia == 'personalizada' and rutina.dias_semana:
            # Verificar si hoy es uno de los días programados
            dias_programados = [d.strip().upper() for d in rutina.dias_semana.split(',')]
            dia_actual = hoy.strftime('%A')[:1].upper()  # L, M, X, J, V, S, D
            if dia_actual in dias_programados and dias_sin_entrenar >= 1:
                necesita_recordatorio = True
        
        if necesita_recordatorio:
            recordatorios.append({
                "rutina": rutina,
                "dias_sin_entrenar": dias_sin_entrenar,
                "ultimo_progreso": ultimo_progreso,
            })
    
    return render(request, "fit/routine_reminders.html", {"recordatorios": recordatorios})

# ==================== FUNCIONALIDADES AVANZADAS PARA ENTRENADORES ====================

# ------------------------- Análisis Detallado de Progreso -------------------------
@login_required
@user_passes_test(is_trainer)
def trainer_progress_analysis(request, user_id):
    """
    Análisis detallado del progreso de un usuario asignado con gráficos y métricas.
    """
    tuser = get_object_or_404(User, pk=user_id)
    trainer = request.user
    
    # Verificar asignación
    assignment = TrainerAssignment.objects.filter(
        trainer=trainer,
        user=tuser,
        activo=True
    ).first()
    
    if not assignment:
        messages.error(request, "Este usuario no está asignado a ti.")
        return redirect("trainer_assignees")
    
    user_info = get_institutional_info(tuser.username)
    
    # Progreso completo del usuario
    all_progress = ProgressLog.objects.filter(user=tuser).order_by("fecha")
    
    # Métricas generales
    total_sesiones = all_progress.count()
    total_tiempo = all_progress.aggregate(Sum("tiempo_seg"))["tiempo_seg__sum"] or 0
    total_tiempo_horas = round(total_tiempo / 3600, 1)
    promedio_esfuerzo = all_progress.aggregate(Avg("esfuerzo"))["esfuerzo__avg"] or 0
    promedio_esfuerzo = round(promedio_esfuerzo, 1)
    
    # Progreso por mes (últimos 6 meses)
    hoy = date.today()
    progreso_mensual = []
    for i in range(6):
        mes_fecha = date(hoy.year, hoy.month - i, 1) if hoy.month > i else date(hoy.year - 1, 12 + hoy.month - i, 1)
        sesiones_mes = all_progress.filter(
            fecha__year=mes_fecha.year,
            fecha__month=mes_fecha.month
        )
        progreso_mensual.append({
            "mes": mes_fecha.strftime("%b %Y"),
            "sesiones": sesiones_mes.count(),
            "tiempo_total": sesiones_mes.aggregate(Sum("tiempo_seg"))["tiempo_seg__sum"] or 0,
            "esfuerzo_promedio": round(sesiones_mes.aggregate(Avg("esfuerzo"))["esfuerzo__avg"] or 0, 1),
        })
    progreso_mensual.reverse()
    
    # Progreso por rutina
    progreso_por_rutina = []
    rutinas_usuario = Routine.objects.filter(user=tuser)
    for rutina in rutinas_usuario:
        progreso_rutina = all_progress.filter(routine=rutina)
        if progreso_rutina.exists():
            progreso_por_rutina.append({
                "rutina": rutina,
                "sesiones": progreso_rutina.count(),
                "ultima_sesion": progreso_rutina.order_by("-fecha").first().fecha,
                "esfuerzo_promedio": round(progreso_rutina.aggregate(Avg("esfuerzo"))["esfuerzo__avg"] or 0, 1),
            })
    
    # Progreso por tipo de ejercicio (basado en rutinas)
    progreso_por_tipo = {}
    for progress in all_progress:
        rutina = progress.routine
        items = rutina.items.all()
        for item in items:
            tipo = item.exercise.tipo
            if tipo not in progreso_por_tipo:
                progreso_por_tipo[tipo] = {"sesiones": 0, "tiempo": 0}
            progreso_por_tipo[tipo]["sesiones"] += 1
            if progress.tiempo_seg:
                progreso_por_tipo[tipo]["tiempo"] += progress.tiempo_seg
    
    # Identificar tendencias y estancamientos
    tendencias = []
    if len(progreso_mensual) >= 2:
        ultimo_mes = progreso_mensual[-1]
        penultimo_mes = progreso_mensual[-2]
        
        if ultimo_mes["sesiones"] > penultimo_mes["sesiones"]:
            tendencias.append({
                "tipo": "positiva",
                "mensaje": f"Mejora en frecuencia: {ultimo_mes['sesiones']} sesiones vs {penultimo_mes['sesiones']} el mes anterior"
            })
        elif ultimo_mes["sesiones"] < penultimo_mes["sesiones"]:
            tendencias.append({
                "tipo": "negativa",
                "mensaje": f"Reducción en frecuencia: {ultimo_mes['sesiones']} sesiones vs {penultimo_mes['sesiones']} el mes anterior"
            })
        
        if ultimo_mes["esfuerzo_promedio"] > penultimo_mes["esfuerzo_promedio"]:
            tendencias.append({
                "tipo": "positiva",
                "mensaje": f"Aumento en intensidad: esfuerzo promedio {ultimo_mes['esfuerzo_promedio']} vs {penultimo_mes['esfuerzo_promedio']}"
            })
    
    # Alertas de bajo rendimiento
    alertas = []
    if total_sesiones > 0:
        ultima_sesion = all_progress.order_by("-fecha").first()
        dias_sin_entrenar = (hoy - ultima_sesion.fecha).days
        
        if dias_sin_entrenar > 7:
            alertas.append({
                "tipo": "inactividad",
                "severidad": "alta" if dias_sin_entrenar > 14 else "media",
                "mensaje": f"Sin actividad durante {dias_sin_entrenar} días"
            })
        
        sesiones_este_mes = all_progress.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        ).count()
        
        if sesiones_este_mes < 4:
            alertas.append({
                "tipo": "baja_frecuencia",
                "severidad": "media",
                "mensaje": f"Solo {sesiones_este_mes} sesiones este mes (recomendado: mínimo 8-12)"
            })
        
        if promedio_esfuerzo < 4:
            alertas.append({
                "tipo": "baja_intensidad",
                "severidad": "baja",
                "mensaje": f"Esfuerzo promedio bajo ({promedio_esfuerzo}/10). Considera aumentar la intensidad."
            })
    
    return render(request, "fit/trainer_progress_analysis.html", {
        "tuser": tuser,
        "user_info": user_info,
        "total_sesiones": total_sesiones,
        "total_tiempo_horas": total_tiempo_horas,
        "promedio_esfuerzo": promedio_esfuerzo,
        "progreso_mensual": progreso_mensual,
        "progreso_por_rutina": progreso_por_rutina,
        "progreso_por_tipo": progreso_por_tipo,
        "tendencias": tendencias,
        "alertas": alertas,
        "all_progress": all_progress[:20],  # Últimas 20 sesiones
    })

# ------------------------- Recomendación Avanzada -------------------------
@login_required
@user_passes_test(is_trainer)
def trainer_recommendation_advanced(request, user_id):
    """
    Sistema avanzado de recomendaciones con ajustes de intensidad/dificultad.
    """
    tuser = get_object_or_404(User, pk=user_id)
    trainer = request.user
    
    # Verificar asignación
    assignment = TrainerAssignment.objects.filter(
        trainer=trainer,
        user=tuser,
        activo=True
    ).first()
    
    if not assignment:
        messages.error(request, "Este usuario no está asignado a ti.")
        return redirect("trainer_assignees")
    
    if request.method == "POST":
        form = TrainerRecommendationForm(request.POST)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.trainer = trainer
            rec.user = tuser
            
            # Campos adicionales si se proporcionan
            routine_id = request.POST.get("routine_id")
            progress_id = request.POST.get("progress_id")
            ajuste_intensidad = request.POST.get("ajuste_intensidad")
            ajuste_dificultad = request.POST.get("ajuste_dificultad")
            
            if routine_id:
                rec.routine = get_object_or_404(Routine, pk=routine_id)
            if progress_id:
                rec.progress_log = get_object_or_404(ProgressLog, pk=progress_id)
            
            rec.save()
            
            # Actualizar estadísticas mensuales
            hoy = date.today()
            stats, _ = TrainerMonthlyStats.objects.get_or_create(
                trainer=trainer,
                anio=hoy.year,
                mes=hoy.month
            )
            stats.seguimientos_realizados += 1
            stats.save()
            
            messages.success(request, "Recomendación enviada correctamente.")
            return redirect("trainer_feedback", user_id=user_id)
    else:
        form = TrainerRecommendationForm()
    
    # Obtener rutinas y progresos del usuario para asociar
    rutinas = Routine.objects.filter(user=tuser)
    progresos_recientes = ProgressLog.objects.filter(user=tuser).order_by("-fecha")[:10]
    
    return render(request, "fit/trainer_recommendation_advanced.html", {
        "tuser": tuser,
        "form": form,
        "rutinas": rutinas,
        "progresos_recientes": progresos_recientes,
    })

# ==================== FUNCIONALIDADES AVANZADAS PARA ADMINISTRADOR ====================

# ------------------------- Gestión de Usuarios -------------------------
@login_required
@user_passes_test(is_admin)
def admin_users_management(request):
    """
    Panel completo de gestión de usuarios con filtros avanzados.
    """
    # Filtros
    search_query = request.GET.get("q", "")
    role_filter = request.GET.get("role", "")
    program_filter = request.GET.get("program", "")
    campus_filter = request.GET.get("campus", "")
    activity_filter = request.GET.get("activity", "")
    
    # Obtener usuarios directamente de la BD institucional
    # Incluir: Estudiantes (STUDENT) y Empleados que NO sean Instructores ni Administrativos (Docentes)
    users_from_db = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT u.username, u.role, u.student_id, u.employee_id
                FROM users u
                WHERE u.is_active = TRUE
                AND u.username NOT LIKE 'test%'
                AND (
                    u.role = 'STUDENT'
                    OR (
                        u.role = 'EMPLOYEE' 
                        AND u.employee_id IS NOT NULL
                        AND EXISTS (
                            SELECT 1 FROM employees e 
                            WHERE e.id = u.employee_id 
                            AND UPPER(e.employee_type) NOT IN ('INSTRUCTOR', 'ADMINISTRATIVO')
                        )
                    )
                )
                ORDER BY u.username
            """)
            for row in cur.fetchall():
                username, role, student_id, employee_id = row
                
                # Filtrar usuarios de prueba
                if 'test' in username.lower():
                    continue
                
                # Aplicar búsqueda si existe
                if search_query and search_query.lower() not in username.lower():
                    continue
                
                # Obtener o crear usuario Django si no existe
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_staff': False, 'is_superuser': False}
                )
                
                # Asegurar que no sea staff ni superuser (son usuarios estándar)
                if not created:
                    if user.is_staff or user.is_superuser:
                        user.is_staff = False
                        user.is_superuser = False
                        user.save()
                
                users_from_db.append(user)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al obtener usuarios de BD institucional: {e}")
        # Fallback: usar solo los que existen en Django
        users_from_db = list(User.objects.filter(is_superuser=False).order_by("username"))
        if search_query:
            users_from_db = [u for u in users_from_db if search_query.lower() in u.username.lower()]
    
    users = users_from_db
    
    # Agregar información institucional y filtrar
    users_with_info = []
    for user in users:
        user_info = get_institutional_info(user.username)
        
        # Filtro por rol
        if role_filter:
            if role_filter == "student" and user_info.get("role") != "STUDENT":
                continue
            elif role_filter == "employee" and user_info.get("role") != "EMPLOYEE":
                continue
            elif role_filter == "trainer" and not user.is_staff:
                continue
        
        # Filtro por programa (solo estudiantes)
        if program_filter and user_info.get("role") == "STUDENT":
            # Aquí necesitarías consultar la tabla students para obtener el programa
            # Por ahora, lo omitimos
            pass
        
        # Filtro por campus
        if campus_filter and user_info.get("campus") != campus_filter:
            continue
        
        # Filtro por actividad
        if activity_filter:
            hoy = date.today()
            sesiones_mes = ProgressLog.objects.filter(
                user=user,
                fecha__year=hoy.year,
                fecha__month=hoy.month
            ).count()
            
            if activity_filter == "high" and sesiones_mes < 10:
                continue
            elif activity_filter == "medium" and (sesiones_mes < 5 or sesiones_mes >= 10):
                continue
            elif activity_filter == "low" and sesiones_mes >= 5:
                continue
            elif activity_filter == "inactive" and sesiones_mes > 0:
                continue
        
        # Estadísticas del usuario
        total_sesiones = ProgressLog.objects.filter(user=user).count()
        rutinas_count = Routine.objects.filter(user=user).count()
        tiene_entrenador = TrainerAssignment.objects.filter(user=user, activo=True).exists()
        
        users_with_info.append({
            "user": user,
            "info": user_info,
            "total_sesiones": total_sesiones,
            "rutinas_count": rutinas_count,
            "tiene_entrenador": tiene_entrenador,
        })
    
    # Obtener opciones para filtros (campus, programas, etc.)
    campuses = []
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT DISTINCT name FROM campuses ORDER BY name")
            campuses = [row[0] for row in cur.fetchall()]
    except Exception:
        pass
    
    return render(request, "fit/admin_users_management.html", {
        "users": users_with_info,
        "search_query": search_query,
        "role_filter": role_filter,
        "program_filter": program_filter,
        "campus_filter": campus_filter,
        "activity_filter": activity_filter,
        "campuses": campuses,
    })

# ------------------------- Asignación Avanzada de Entrenadores -------------------------
@login_required
@user_passes_test(is_admin)
def admin_assign_trainer_advanced(request):
    """
    Sistema avanzado de asignación de entrenadores con gestión de carga de trabajo.
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        trainer_id = request.POST.get("trainer_id")
        accion = request.POST.get("accion")
        
        if user_id and trainer_id:
            user = get_object_or_404(User, pk=user_id)
            trainer = get_object_or_404(User, pk=trainer_id)
            
            if accion == "asignar":
                # Verificar si ya existe una asignación activa
                existing = TrainerAssignment.objects.filter(
                    user=user, trainer=trainer, activo=True
                ).first()
                
                if existing:
                    messages.info(request, f"El usuario {user.username} ya tiene asignado a {trainer.username}.")
                else:
                    # Desactivar otras asignaciones activas del mismo usuario
                    TrainerAssignment.objects.filter(user=user, activo=True).update(activo=False)
                    
                    # Crear nueva asignación
                    assignment = TrainerAssignment.objects.create(
                        user=user,
                        trainer=trainer,
                        activo=True
                    )
                    
                    # Registrar en historial
                    AssignmentHistory.objects.create(
                        assignment=assignment,
                        accion="creada",
                        administrador=request.user,
                        notas=f"Asignación creada por {request.user.username}"
                    )
                    
                    messages.success(request, f"Entrenador {trainer.username} asignado a {user.username}.")
            
            elif accion == "desactivar":
                assignment = TrainerAssignment.objects.filter(
                    user=user, trainer=trainer, activo=True
                ).first()
                
                if assignment:
                    assignment.activo = False
                    assignment.save()
                    
                    # Registrar en historial
                    AssignmentHistory.objects.create(
                        assignment=assignment,
                        accion="desactivada",
                        administrador=request.user,
                        notas=f"Asignación desactivada por {request.user.username}"
                    )
                    
                    messages.success(request, f"Asignación desactivada.")
    
    # Obtener usuarios directamente de la BD institucional
    # Incluir: Estudiantes (STUDENT) y Empleados que NO sean Instructores ni Administrativos (Docentes)
    usuarios_from_db = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT u.username, u.role, u.student_id, u.employee_id
                FROM users u
                WHERE u.is_active = TRUE
                AND u.username NOT LIKE 'test%'
                AND (
                    u.role = 'STUDENT'
                    OR (
                        u.role = 'EMPLOYEE' 
                        AND u.employee_id IS NOT NULL
                        AND EXISTS (
                            SELECT 1 FROM employees e 
                            WHERE e.id = u.employee_id 
                            AND UPPER(e.employee_type) NOT IN ('INSTRUCTOR', 'ADMINISTRATIVO')
                        )
                    )
                )
                ORDER BY u.username
            """)
            for row in cur.fetchall():
                username, role, student_id, employee_id = row
                
                # Filtrar usuarios de prueba
                if 'test' in username.lower():
                    continue
                
                # Obtener o crear usuario Django si no existe
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_staff': False, 'is_superuser': False}
                )
                
                # Asegurar que no sea staff ni superuser (son usuarios estándar)
                if not created:
                    if user.is_staff or user.is_superuser:
                        user.is_staff = False
                        user.is_superuser = False
                        user.save()
                
                usuarios_from_db.append(user)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al obtener usuarios de BD institucional: {e}")
        # Fallback: usar solo los que existen en Django
        usuarios_from_db = list(User.objects.filter(is_staff=False, is_superuser=False).order_by("username"))
    
    usuarios = usuarios_from_db
    # Obtener solo Instructores (entrenadores reales)
    entrenadores = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT u.username
                FROM users u
                JOIN employees e ON u.employee_id = e.id
                WHERE u.role = 'EMPLOYEE'
                AND UPPER(e.employee_type) = 'INSTRUCTOR'
                ORDER BY e.last_name, e.first_name
            """)
            trainer_usernames = [row[0] for row in cur.fetchall()]
            entrenadores = User.objects.filter(username__in=trainer_usernames).order_by("username")
    except Exception:
        entrenadores = User.objects.none()
    
    # Agregar información de carga de trabajo para entrenadores
    entrenadores_con_carga = []
    for trainer in entrenadores:
        asignados_activos = TrainerAssignment.objects.filter(trainer=trainer, activo=True).count()
        entrenadores_con_carga.append({
            "trainer": trainer,
            "asignados_activos": asignados_activos,
            "info": get_institutional_info(trainer.username),
        })
    
    # Agregar información de asignaciones para usuarios
    usuarios_con_info = []
    for user in usuarios:
        asignaciones = TrainerAssignment.objects.filter(user=user, activo=True).select_related("trainer")
        usuarios_con_info.append({
            "user": user,
            "info": get_institutional_info(user.username),
            "asignaciones": asignaciones,
        })
    
    return render(request, "fit/admin_assign_trainer_advanced.html", {
        "usuarios": usuarios_con_info,
        "entrenadores": entrenadores_con_carga,
    })

@login_required
@user_passes_test(is_admin)
def admin_assignment_history(request):
    """
    Historial completo de cambios en asignaciones.
    """
    historial = AssignmentHistory.objects.select_related(
        "assignment", "assignment__user", "assignment__trainer", "administrador"
    ).order_by("-fecha")
    
    # Filtros
    user_filter = request.GET.get("user", "")
    trainer_filter = request.GET.get("trainer", "")
    accion_filter = request.GET.get("accion", "")
    
    if user_filter:
        historial = historial.filter(assignment__user__username__icontains=user_filter)
    if trainer_filter:
        historial = historial.filter(assignment__trainer__username__icontains=trainer_filter)
    if accion_filter:
        historial = historial.filter(accion=accion_filter)
    
    return render(request, "fit/admin_assignment_history.html", {
        "historial": historial,
        "user_filter": user_filter,
        "trainer_filter": trainer_filter,
        "accion_filter": accion_filter,
    })

# ------------------------- Gestión de Contenido Global -------------------------
@login_required
@user_passes_test(is_admin)
def admin_content_moderation(request):
    """
    Panel de moderación de ejercicios y rutinas.
    """
    # Ejercicios pendientes de moderación
    ejercicios_pendientes = Exercise.objects.filter(
        es_personalizado=True
    ).exclude(
        id__in=ContentModeration.objects.filter(
            tipo_contenido="exercise", estado="aprobado"
        ).values_list("contenido_id", flat=True)
    )
    
    # Rutinas pendientes de moderación
    rutinas_pendientes = Routine.objects.filter(
        es_predisenada=True
    ).exclude(
        id__in=ContentModeration.objects.filter(
            tipo_contenido="routine", estado="aprobado"
        ).values_list("contenido_id", flat=True)
    )
    
    # Contenido moderado recientemente
    moderaciones_recientes = ContentModeration.objects.select_related("moderador").order_by("-fecha_revision")[:20]
    
    return render(request, "fit/admin_content_moderation.html", {
        "ejercicios_pendientes": ejercicios_pendientes,
        "rutinas_pendientes": rutinas_pendientes,
        "moderaciones_recientes": moderaciones_recientes,
    })

@login_required
@user_passes_test(is_admin)
def admin_moderate_content(request, tipo, contenido_id):
    """
    Aprobar o rechazar contenido específico.
    """
    if request.method == "POST":
        accion = request.POST.get("accion")
        comentarios = request.POST.get("comentarios", "")
        
        # Obtener o crear registro de moderación
        moderacion, created = ContentModeration.objects.get_or_create(
            tipo_contenido=tipo,
            contenido_id=contenido_id,
            defaults={"estado": "pendiente"}
        )
        
        if accion == "aprobar":
            moderacion.estado = "aprobado"
            moderacion.moderador = request.user
            moderacion.fecha_revision = timezone.now()
            moderacion.comentarios = comentarios
            moderacion.save()
            messages.success(request, "Contenido aprobado correctamente.")
        elif accion == "rechazar":
            moderacion.estado = "rechazado"
            moderacion.moderador = request.user
            moderacion.fecha_revision = timezone.now()
            moderacion.comentarios = comentarios
            moderacion.save()
            
            # Opcional: eliminar el contenido rechazado
            if tipo == "exercise":
                Exercise.objects.filter(id=contenido_id).delete()
            elif tipo == "routine":
                Routine.objects.filter(id=contenido_id).delete()
            
            messages.success(request, "Contenido rechazado y eliminado.")
        elif accion == "editar":
            moderacion.estado = "editado"
            moderacion.moderador = request.user
            moderacion.fecha_revision = timezone.now()
            moderacion.comentarios = comentarios
            moderacion.save()
            messages.success(request, "Contenido marcado como editado.")
        
        return redirect("admin_content_moderation")
    
    # Obtener el contenido
    if tipo == "exercise":
        contenido = get_object_or_404(Exercise, pk=contenido_id)
    elif tipo == "routine":
        contenido = get_object_or_404(Routine, pk=contenido_id)
    else:
        messages.error(request, "Tipo de contenido inválido.")
        return redirect("admin_content_moderation")
    
    return render(request, "fit/admin_moderate_content.html", {
        "tipo": tipo,
        "contenido": contenido,
    })

# ------------------------- Reportes y Analytics Avanzados -------------------------
@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    """
    Reportes y analytics avanzados del sistema.
    """
    hoy = date.today()
    
    # Métricas generales del sistema
    total_usuarios = User.objects.filter(is_staff=False, is_superuser=False).count()
    # Contar solo Instructores (entrenadores reales)
    total_entrenadores = 0
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM employees 
                WHERE UPPER(employee_type) = 'INSTRUCTOR'
            """)
            row = cur.fetchone()
            if row:
                total_entrenadores = row[0]
    except Exception:
        pass
    
    total_rutinas = Routine.objects.count()
    total_ejercicios = Exercise.objects.count()
    total_sesiones = ProgressLog.objects.count()
    
    # Actividad por mes (últimos 12 meses)
    actividad_mensual = []
    for i in range(12):
        mes_fecha = date(hoy.year, hoy.month - i, 1) if hoy.month > i else date(hoy.year - 1, 12 + hoy.month - i, 1)
        sesiones_mes = ProgressLog.objects.filter(
            fecha__year=mes_fecha.year,
            fecha__month=mes_fecha.month
        ).count()
        usuarios_activos_mes = ProgressLog.objects.filter(
            fecha__year=mes_fecha.year,
            fecha__month=mes_fecha.month
        ).values("user").distinct().count()
        actividad_mensual.append({
            "mes": mes_fecha.strftime("%b %Y"),
            "sesiones": sesiones_mes,
            "usuarios_activos": usuarios_activos_mes,
        })
    actividad_mensual.reverse()
    
    # Actividad por facultad/departamento
    actividad_por_facultad = {}
    try:
        with connection.cursor() as cur:
            # Obtener sesiones de usuarios con información de facultad
            cur.execute("""
                SELECT f.name, COUNT(DISTINCT pl.user_id) as usuarios_activos, COUNT(pl.id) as sesiones
                FROM fit_progresslog pl
                JOIN auth_user u ON pl.user_id = u.id
                JOIN users usr ON u.username = usr.username
                LEFT JOIN students s ON usr.student_id = s.id
                LEFT JOIN employees e ON usr.employee_id = e.id
                LEFT JOIN faculties f ON COALESCE(s.faculty_code, e.faculty_code) = f.code
                WHERE pl.fecha >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY f.name
                ORDER BY sesiones DESC
            """)
            for row in cur.fetchall():
                if row[0]:  # Si hay nombre de facultad
                    actividad_por_facultad[row[0]] = {
                        "usuarios_activos": row[1],
                        "sesiones": row[2],
                    }
    except Exception:
        pass
    
    # Efectividad de entrenadores (solo Instructores)
    efectividad_entrenadores = []
    # Obtener solo Instructores
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT u.username
                FROM users u
                JOIN employees e ON u.employee_id = e.id
                WHERE u.role = 'EMPLOYEE'
                AND UPPER(e.employee_type) = 'INSTRUCTOR'
            """)
            trainer_usernames = [row[0] for row in cur.fetchall()]
            entrenadores = User.objects.filter(username__in=trainer_usernames)
    except Exception:
        entrenadores = User.objects.none()
    for trainer in entrenadores:
        asignados = TrainerAssignment.objects.filter(trainer=trainer, activo=True).count()
        if asignados > 0:
            # Progreso promedio de usuarios asignados
            usuarios_asignados = TrainerAssignment.objects.filter(
                trainer=trainer, activo=True
            ).values_list("user_id", flat=True)
            
            sesiones_totales = ProgressLog.objects.filter(
                user_id__in=usuarios_asignados
            ).count()
            
            recomendaciones = TrainerRecommendation.objects.filter(trainer=trainer).count()
            
            efectividad_entrenadores.append({
                "trainer": trainer,
                "info": get_institutional_info(trainer.username),
                "asignados": asignados,
                "sesiones_totales": sesiones_totales,
                "recomendaciones": recomendaciones,
                "promedio_sesiones_por_usuario": round(sesiones_totales / asignados, 1) if asignados > 0 else 0,
            })
    
    efectividad_entrenadores.sort(key=lambda x: x["promedio_sesiones_por_usuario"], reverse=True)
    
    # Popularidad de ejercicios
    popularidad_ejercicios = RoutineItem.objects.values(
        "exercise__nombre", "exercise__tipo"
    ).annotate(
        veces_usado=Count("id")
    ).order_by("-veces_usado")[:10]
    
    # Popularidad de rutinas
    popularidad_rutinas = ProgressLog.objects.values(
        "routine__nombre"
    ).annotate(
        veces_usada=Count("id")
    ).order_by("-veces_usada")[:10]
    
    # Tendencias temporales
    tendencias = {
        "crecimiento_usuarios": total_usuarios,  # Simplificado
        "crecimiento_sesiones": total_sesiones,  # Simplificado
    }
    
    return render(request, "fit/admin_analytics.html", {
        "total_usuarios": total_usuarios,
        "total_entrenadores": total_entrenadores,
        "total_rutinas": total_rutinas,
        "total_ejercicios": total_ejercicios,
        "total_sesiones": total_sesiones,
        "actividad_mensual": actividad_mensual,
        "actividad_por_facultad": actividad_por_facultad,
        "efectividad_entrenadores": efectividad_entrenadores,
        "popularidad_ejercicios": popularidad_ejercicios,
        "popularidad_rutinas": popularidad_rutinas,
        "tendencias": tendencias,
    })

# ------------------------- Configuración del Sistema -------------------------
@login_required
@user_passes_test(is_admin)
def admin_system_config(request):
    """
    Configuración global del sistema.
    """
    if request.method == "POST":
        clave = request.POST.get("clave")
        valor = request.POST.get("valor")
        descripcion = request.POST.get("descripcion", "")
        accion = request.POST.get("accion")
        
        if accion == "crear" and clave and valor:
            config, created = SystemConfig.objects.get_or_create(
                clave=clave,
                defaults={"valor": valor, "descripcion": descripcion}
            )
            if not created:
                config.valor = valor
                config.descripcion = descripcion
                config.save()
            messages.success(request, f"Configuración '{clave}' guardada.")
        elif accion == "eliminar":
            config_id = request.POST.get("config_id")
            SystemConfig.objects.filter(id=config_id).delete()
            messages.success(request, "Configuración eliminada.")
        
        return redirect("admin_system_config")
    
    configs = SystemConfig.objects.all().order_by("clave")
    
    return render(request, "fit/admin_system_config.html", {
        "configs": configs,
    })
