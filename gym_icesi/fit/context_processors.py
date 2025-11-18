# fit/context_processors.py
from django.db import connection
from .models import TrainerAssignment

def nav_trainers(request):
    """
    Inserta 'nav_trainers' en el contexto global SOLO para staff/superuser.
    """
    trainers = []
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        try:
            with connection.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.first_name, e.last_name
                    FROM employees e
                    WHERE UPPER(e.employee_type) IN ('TRAINER', 'ENTRENADOR')
                    ORDER BY e.last_name
                    LIMIT 10
                """)
                for (emp_id, fn, ln) in cur.fetchall():
                    trainers.append({"id": emp_id, "name": f"{fn} {ln}"})
        except Exception:
            # Si falla (por ejemplo, usando SQLite sin BD institucional), continuar sin trainers
            pass
    return {"nav_trainers": trainers}


def user_context(request):
    """
    Contexto global para usuarios autenticados
    """
    context = {}
    if request.user.is_authenticated:
        # Verificar si el usuario tiene entrenador asignado
        has_trainer = TrainerAssignment.objects.filter(
            user=request.user, activo=True
        ).exists()
        context["has_trainer"] = has_trainer
    return context
