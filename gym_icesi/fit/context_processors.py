# fit/context_processors.py
from django.db import connection

def nav_trainers(request):
    """
    Inserta 'nav_trainers' en el contexto global SOLO para staff/superuser.
    """
    trainers = []
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
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
    return {"nav_trainers": trainers}
