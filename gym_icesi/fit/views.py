# fit/views.py
from datetime import date
from calendar import monthrange

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Exercise,
    Routine,
    RoutineItem,
    ProgressLog,
    TrainerAssignment,
    UserMonthlyStats,
    TrainerMonthlyStats,
)
from .forms import RoutineForm, RoutineItemForm, ProgressForm
from fit.institutional_models import InstitutionalUser


# ----------------------------- Aux institucional -----------------------------
def get_institutional_info(username):
    data = {}
    try:
        iu = InstitutionalUser.objects.get(username=username, is_active=True)
        data["role"] = iu.role
        data["student_id"] = iu.student_id
        data["employee_id"] = iu.employee_id

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
    r = get_object_or_404(Routine, pk=pk, user=request.user)
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
            messages.success(request, "Progreso registrado.")
            return redirect("home")
    else:
        form = ProgressForm()
        form.fields["routine"].queryset = Routine.objects.filter(user=request.user)
    return render(request, "fit/progress_form.html", {"form": form})


# ------------------------- Entrenadores institucionales ----------------------
@login_required
def trainers_view(request):
    """
    Vista simple de entrenadores institucionales (consulta directa a employees).
    """
    trainers = []
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT e.id, e.first_name, e.last_name, e.email, f.name AS faculty
            FROM employees e
            JOIN faculties f ON e.faculty_code = f.code
            WHERE UPPER(e.employee_type) IN ('TRAINER', 'ENTRENADOR', 'ENTRENADOR PERSONAL')
            ORDER BY e.last_name, e.first_name;
            """
        )
        for (emp_id, fn, ln, email, faculty) in cur.fetchall():
            trainers.append(
                {
                    "id": emp_id,
                    "name": f"{fn} {ln}",
                    "email": email,
                    "faculty": faculty,
                }
            )
    return render(request, "fit/trainers.html", {"trainers": trainers})


@login_required
def trainer_detail(request, emp_id: str):
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
    )
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
    return render(
        request,
        "fit/trainer_feedback.html",
        {"tuser": tuser, "progress": progress, "routines": routines},
    )


@login_required
@user_passes_test(is_admin)
def trainers_list(request):
    """
    Lista SOLO los entrenadores reales desde EMPLOYEES,
    filtrando por employee_type = 'INSTRUCTOR'.
    """
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

    return render(request, "fit/trainers_list.html", {"trainers": trainers})


@login_required
def trainers_view(request):
    """
    Vista para cualquier usuario logueado:
    muestra SOLO los empleados cuyo employee_type = 'INSTRUCTOR'.
    """
    trainers = []
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

    return render(request, "fit/trainers.html", {"trainers": trainers})



# ------------------------------- Reportes/Admin ------------------------------
@login_required
def report_adherence(request):
    hoy = date.today()
    anio, mes = hoy.year, hoy.month
    inicio = date(anio, mes, 1)
    fin = date(anio, mes, monthrange(anio, mes)[1])

    logs = ProgressLog.objects.filter(user=request.user, fecha__range=(inicio, fin))
    dias_activos = logs.values("fecha").distinct().count()
    por_tipo = (
        logs.values("routine__items__exercise__tipo")
        .annotate(sesiones=Count("id"))
        .order_by()
    )

    return render(
        request,
        "fit/report_adherence.html",
        {
            "dias_activos": dias_activos,
            "por_tipo": por_tipo,
            "periodo": (inicio, fin),
        },
    )


@login_required
def report_load_balance(request):
    agg = (
        ProgressLog.objects.filter(user=request.user)
        .values("routine__items__exercise__tipo")
        .annotate(
            total_reps=Sum("repeticiones"),
            total_tiempo=Sum("tiempo_seg"),
        )
        .order_by()
    )
    return render(request, "fit/report_load_balance.html", {"agg": agg})


@login_required
@user_passes_test(is_admin)
def admin_assign_trainer(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        trainer_id = request.POST.get("trainer_id")
        user = get_object_or_404(User, pk=user_id)
        trainer = get_object_or_404(User, pk=trainer_id, is_staff=True)

        TrainerAssignment.objects.update_or_create(
            user=user,
            activo=True,
            defaults={"trainer": trainer},
        )
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
