# fit/views.py
from datetime import date, timedelta
from calendar import monthrange

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Sum, Max, Avg, Q
from django.db import models as django_models
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
)
from .forms import RoutineForm, RoutineItemForm, ProgressForm, ExerciseForm, TrainerRecommendationForm
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
    
    # Si es entrenador, mostrar dashboard de entrenador
    if user.is_staff:
        return trainer_dashboard(request)
    
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
    sesiones_usuarios_mes = ProgressLog.objects.filter(
        routine__user__trainerassignment__trainer=user,
        routine__user__trainerassignment__activo=True,
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
    total_entrenadores = User.objects.filter(is_staff=True, is_superuser=False).count()
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
    return u.is_staff


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
    muestra SOLO los empleados cuyo employee_type = 'INSTRUCTOR'.
    """
    trainers = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT e.id,
                       e.first_name,
                       e.last_name,
                       e.email,
                       f.name AS faculty
                FROM employees e
                JOIN faculties f ON e.faculty_code = f.code
                WHERE UPPER(e.employee_type) = 'INSTRUCTOR'
                ORDER BY e.last_name, e.first_name;
            """)
            for (emp_id, fn, ln, email, faculty) in cur.fetchall():
                trainers.append({
                    "id": emp_id,
                    "name": f"{fn} {ln}",
                    "email": email,
                    "faculty": faculty,
                })
    except Exception:
        # Si falla (por ejemplo, usando SQLite sin BD institucional), mostrar lista vacía
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
        trainer = get_object_or_404(User, pk=trainer_id, is_staff=True, is_superuser=False)

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
    
    users_query = User.objects.filter(is_staff=False, is_superuser=False)
    if search_user:
        users_query = users_query.filter(username__icontains=search_user)
    users = users_query.order_by("username")[:50]
    
    # Agregar información institucional a usuarios
    users_with_info = []
    for user in users:
        user_info = get_institutional_info(user.username)
        # Obtener asignación actual
        current_assignment = TrainerAssignment.objects.filter(
            user=user, activo=True
        ).select_related("trainer").first()
        
        users_with_info.append({
            "user": user,
            "user_info": user_info,
            "current_assignment": current_assignment,
        })
    
    # Búsqueda de entrenadores
    trainers_query = User.objects.filter(is_staff=True, is_superuser=False)
    if search_trainer:
        trainers_query = trainers_query.filter(username__icontains=search_trainer)
    trainers = trainers_query.order_by("username")
    
    # Agregar información institucional a entrenadores
    trainers_with_info = []
    for trainer in trainers:
        trainer_info = get_institutional_info(trainer.username)
        # Contar usuarios asignados
        asignados_count = TrainerAssignment.objects.filter(
            trainer=trainer, activo=True
        ).count()
        
        trainers_with_info.append({
            "trainer": trainer,
            "trainer_info": trainer_info,
            "asignados_count": asignados_count,
        })

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
