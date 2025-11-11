# fit/institutional_models.py
from django.db import models

class InstitutionalUser(models.Model):
    username = models.CharField(primary_key=True, max_length=30)
    password_hash = models.CharField(max_length=100)
    role = models.CharField(max_length=20)  # STUDENT | EMPLOYEE | ADMIN
    student_id = models.CharField(max_length=15, null=True, blank=True)
    employee_id = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'
