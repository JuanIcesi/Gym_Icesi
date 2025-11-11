from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import date
from calendar import monthrange
from .models import Exercise, Routine, RoutineItem, ProgressLog, TrainerAssignment, UserMonthlyStats, TrainerMonthlyStats
from .forms import RoutineForm, RoutineItemForm, ProgressForm

@login_required
def home(request):
    user = request.user

    # Obtener últimas sesiones y rutinas
    latest = ProgressLog.objects.filter(user=user).order_by('-fecha')[:5]
    my_routines = Routine.objects.filter(user=user).order_by('-fecha_creacion')[:5]

    # Estadísticas generales
    total_routines = Routine.objects.filter(user=user).count()
    total_sessions = ProgressLog.objects.filter(user=user).count()

    # Estadísticas del mes actual
    today = date.today()
    current_month_sessions = ProgressLog.objects.filter(
        user=user,
        fecha__year=today.year,
        fecha__month=today.month
    )
    monthly_count = current_month_sessions.count()

    # Días activos este mes
    active_days = current_month_sessions.values('fecha').distinct().count()

    # Esfuerzo promedio
    avg_effort = current_month_sessions.aggregate(avg=Sum('esfuerzo'))['avg'] or 0
    if monthly_count > 0:
        avg_effort = round(avg_effort / monthly_count, 1)

    context = {
        'latest': latest,
        'my_routines': my_routines,
        'total_routines': total_routines,
        'total_sessions': total_sessions,
        'monthly_count': monthly_count,
        'active_days': active_days,
        'avg_effort': avg_effort,
    }
    return render(request, 'fit/home.html', context)

@login_required
def routine_list(request):
    routines = Routine.objects.filter(user=request.user).order_by('-fecha_creacion')
    presets = Routine.objects.filter(es_predisenada=True).order_by('nombre')[:10]
    return render(request, 'fit/routine_list.html', {'routines': routines, 'presets': presets})

@login_required
def routine_create(request):
    if request.method == 'POST':
        form = RoutineForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.user = request.user
            r.save()
            messages.success(request, 'Rutina creada.')
            return redirect('routine_detail', pk=r.pk)
    else:
        form = RoutineForm()
    return render(request, 'fit/routine_form.html', {'form': form})

@login_required
def routine_detail(request, pk):
    r = get_object_or_404(Routine, pk=pk)
    if r.user != request.user and not r.es_predisenada:
        messages.error(request, 'No puedes ver esta rutina.')
        return redirect('routine_list')
    items = r.items.select_related('exercise').all()
    return render(request, 'fit/routine_detail.html', {'routine': r, 'items': items})

@login_required
def routine_add_item(request, pk):
    r = get_object_or_404(Routine, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RoutineItemForm(request.POST)
        if form.is_valid():
            it = form.save(commit=False)
            it.routine = r
            # Validación simple: al menos reps/series o tiempo
            if not it.tiempo_seg and not (it.series and it.reps):
                messages.error(request, 'Define tiempo (seg) o series/reps.')
                return render(request, 'fit/routine_item_form.html', {'form': form, 'routine': r})
            it.save()
            return redirect('routine_detail', pk=pk)
    else:
        form = RoutineItemForm()
    return render(request, 'fit/routine_item_form.html', {'form': form, 'routine': r})

@login_required
def routine_adopt(request, pk):
    preset = get_object_or_404(Routine, pk=pk, es_predisenada=True)
    nueva = Routine.objects.create(user=request.user, nombre=f'{preset.nombre} (mi copia)')
    for i in preset.items.all():
        RoutineItem.objects.create(
            routine=nueva, exercise=i.exercise, orden=i.orden,
            series=i.series, reps=i.reps, tiempo_seg=i.tiempo_seg, notas=i.notas
        )
    messages.success(request, 'Rutina adoptada.')
    return redirect('routine_detail', pk=nueva.pk)

@login_required
def progress_create(request):
    if request.method == 'POST':
        form = ProgressForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            if p.routine.user != request.user:
                messages.error(request, 'Rutina inválida.')
                return redirect('progress_create')
            p.user = request.user
            p.save()
            messages.success(request, 'Progreso registrado.')
            return redirect('home')
    else:
        form = ProgressForm()
        form.fields['routine'].queryset = Routine.objects.filter(user=request.user)
    return render(request, 'fit/progress_form.html', {'form': form})

def is_trainer(u):
    return u.is_staff

@login_required
@user_passes_test(is_trainer)
def trainer_assignees(request):
    asignados = TrainerAssignment.objects.filter(trainer=request.user, activo=True).select_related('user')
    return render(request, 'fit/trainer_assignees.html', {'asignados': asignados})

@login_required
@user_passes_test(is_trainer)
def trainer_feedback(request, user_id):
    tuser = get_object_or_404(User, pk=user_id)
    progress = ProgressLog.objects.filter(user=tuser).order_by('-fecha')[:20]
    routines = Routine.objects.filter(user=tuser)
    return render(request, 'fit/trainer_feedback.html', {'tuser': tuser, 'progress': progress, 'routines': routines})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_assign_trainer(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        trainer_id = request.POST.get('trainer_id')
        user = get_object_or_404(User, pk=user_id)
        trainer = get_object_or_404(User, pk=trainer_id, is_staff=True)
        TrainerAssignment.objects.update_or_create(user=user, activo=True, defaults={'trainer': trainer})
        messages.success(request, 'Asignación guardada.')
        return redirect('admin_assign_trainer')
    users = User.objects.filter(is_staff=False).order_by('username')[:100]
    trainers = User.objects.filter(is_staff=True).order_by('username')
    return render(request, 'fit/admin_assign_trainer.html', {'users': users, 'trainers': trainers})

@login_required
def report_adherence(request):
    hoy = date.today()
    anio, mes = hoy.year, hoy.month
    inicio = date(anio, mes, 1)
    fin = date(anio, mes, monthrange(anio, mes)[1])
    logs = ProgressLog.objects.filter(user=request.user, fecha__range=(inicio, fin))
    dias_activos = logs.values('fecha').distinct().count()
    por_tipo = logs.values('routine__items__exercise__tipo').annotate(sesiones=Count('id')).order_by()
    return render(request, 'fit/report_adherence.html', {
        'dias_activos': dias_activos,
        'por_tipo': por_tipo, 'periodo': (inicio, fin)
    })

@login_required
def report_load_balance(request):
    agg = (ProgressLog.objects
           .filter(user=request.user)
           .values('routine__items__exercise__tipo')
           .annotate(total_reps=Sum('repeticiones'), total_tiempo=Sum('tiempo_seg'))
           .order_by())
    return render(request, 'fit/report_load_balance.html', {'agg': agg})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def recalc_stats_month(request):
    hoy = date.today()
    anio, mes = hoy.year, hoy.month
    ui, _ = UserMonthlyStats.objects.get_or_create(user=request.user, anio=anio, mes=mes)
    ui.seguimientos_registrados = ProgressLog.objects.filter(user=request.user, fecha__year=anio, fecha__month=mes).count()
    ui.rutinas_iniciadas = Routine.objects.filter(user=request.user, fecha_creacion__year=anio, fecha_creacion__month=mes).count()
    ui.save()
    messages.success(request, 'Stats actualizadas para tu usuario.')
    return redirect('home')
