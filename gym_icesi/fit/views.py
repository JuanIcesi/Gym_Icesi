# fit/views.py
from datetime import date, timedelta
from calendar import monthrange

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Sum, Max, Avg
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

    latest = ProgressLog.objects.filter(user=user).order_by("-fecha")[:5]
    my_routines = Routine.objects.filter(user=user).order_by("-fecha_creacion")[:5]

    total_routines = Routine.objects.filter(user=user).count()
    total_sessions = ProgressLog.objects.filter(user=user).count()

    today = date.today()
    current_month_sessions = ProgressLog.objects.filter(
        user=user, fecha__year=today.year, fecha__month=today.month
    )
    monthly_count = current_month_sessions.count()
    active_days = current_month_sessions.values("fecha").distinct().count()
    avg_effort = current_month_sessions.aggregate(avg=Sum("esfuerzo"))["avg"] or 0
    if monthly_count:
        avg_effort = round(avg_effort / monthly_count, 1)
    
    # Recomendaciones no leídas
    unread_recommendations = TrainerRecommendation.objects.filter(
        user=user,
        leido=False
    ).count()

    return render(
        request,
        "fit/home.html",
        {
            "info": info,
            "latest": latest,
            "my_routines": my_routines,
            "total_routines": total_routines,
            "total_sessions": total_sessions,
            "monthly_count": monthly_count,
            "active_days": active_days,
            "avg_effort": avg_effort,
            "unread_recommendations": unread_recommendations,
        },
    )


# ------------------------------- Rutinas ------------------------------------
@login_required
def routine_list(request):
    routines = Routine.objects.filter(user=request.user).order_by("-fecha_creacion")
    presets = (
        Routine.objects.filter(es_predisenada=True).order_by("nombre")[:10]
    )
    return render(
        request,
        "fit/routine_list.html",
        {"routines": routines, "presets": presets},
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
    r = get_object_or_404(Routine, pk=pk)
    # Permitir agregar items si es el dueño o si es entrenador y es rutina prediseñada
    if r.user != request.user and not (request.user.is_staff and r.es_predisenada and r.autor_trainer == request.user):
        messages.error(request, "No tienes permiso para modificar esta rutina.")
        return redirect("routine_detail", pk=pk)
    
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
    if request.method == "POST":
        form = ProgressForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            if p.routine.user != request.user:
                messages.error(request, "Rutina inválida.")
                return redirect("progress_create")
            p.user = request.user
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
            messages.success(request, "Progreso registrado.")
            return redirect("home")
    else:
        form = ProgressForm()
        form.fields["routine"].queryset = Routine.objects.filter(user=request.user)
    return render(request, "fit/progress_form.html", {"form": form})


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
    # puedes ajustar si quieres que solo superuser pueda ver algunas cosas
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_trainer)
def trainer_assignees(request):
    asignados = (
        TrainerAssignment.objects.filter(trainer=request.user, activo=True)
        .select_related("user")
        .prefetch_related("user__routines", "user__progress")
        .order_by("-fecha_asignacion")
    )
    # Agregar información de último progreso para cada asignado
    for asignado in asignados:
        last_progress = asignado.user.progress.order_by("-fecha").first()
        asignado.last_progress_date = last_progress.fecha if last_progress else None
    
    return render(
        request,
        "fit/trainer_assignees.html",
        {"asignados": asignados},
    )


@login_required
@user_passes_test(is_trainer)
def trainer_feedback(request, user_id):
    tuser = get_object_or_404(User, pk=user_id)
    progress = ProgressLog.objects.filter(user=tuser).order_by("-fecha")[:20]
    routines = Routine.objects.filter(user=tuser)
    recommendations = TrainerRecommendation.objects.filter(
        trainer=request.user,
        user=tuser
    ).order_by("-fecha")[:10]
    
    # Verificar asignación
    assignment = TrainerAssignment.objects.filter(
        trainer=request.user,
        user=tuser,
        activo=True
    ).first()
    
    return render(
        request,
        "fit/trainer_feedback.html",
        {
            "tuser": tuser,
            "progress": progress,
            "routines": routines,
            "recommendations": recommendations,
            "assignment": assignment,
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
    """Reporte mejorado de adherencia con más métricas"""
    hoy = date.today()
    anio, mes = hoy.year, hoy.month
    inicio = date(anio, mes, 1)
    fin = date(anio, mes, monthrange(anio, mes)[1])

    logs = ProgressLog.objects.filter(user=request.user, fecha__range=(inicio, fin))
    dias_activos = logs.values("fecha").distinct().count()
    total_sesiones = logs.count()
    dias_del_mes = monthrange(anio, mes)[1]
    porcentaje_adherencia = round((dias_activos / dias_del_mes) * 100, 1) if dias_del_mes > 0 else 0
    
    por_tipo = (
        logs.values("routine__items__exercise__tipo")
        .annotate(sesiones=Count("id"))
        .order_by()
    )
    
    # Esfuerzo promedio
    esfuerzo_promedio = logs.aggregate(avg=Sum("esfuerzo"))["avg"] or 0
    if total_sesiones > 0:
        esfuerzo_promedio = round(esfuerzo_promedio / total_sesiones, 1)
    
    # Rutinas más usadas
    rutinas_mas_usadas = (
        logs.values("routine__nombre")
        .annotate(veces=Count("id"))
        .order_by("-veces")[:5]
    )

    return render(
        request,
        "fit/report_adherence.html",
        {
            "dias_activos": dias_activos,
            "total_sesiones": total_sesiones,
            "dias_del_mes": dias_del_mes,
            "porcentaje_adherencia": porcentaje_adherencia,
            "esfuerzo_promedio": esfuerzo_promedio,
            "por_tipo": por_tipo,
            "rutinas_mas_usadas": rutinas_mas_usadas,
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
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        trainer_id = request.POST.get("trainer_id")
        user = get_object_or_404(User, pk=user_id)
        trainer = get_object_or_404(User, pk=trainer_id, is_staff=True)

        assignment, created = TrainerAssignment.objects.update_or_create(
            user=user,
            activo=True,
            defaults={"trainer": trainer},
        )

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

        messages.success(request, "Asignación guardada.")
        return redirect("admin_assign_trainer")

    users = User.objects.filter(is_staff=False).order_by("username")[:100]
    trainers = User.objects.filter(is_staff=True).order_by("username")

    return render(
        request,
        "fit/admin_assign_trainer.html",
        {"users": users, "trainers": trainers},
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
