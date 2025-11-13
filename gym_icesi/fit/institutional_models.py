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

    def __str__(self):
        return f"{self.username} ({self.role})"


class Employee(models.Model):
    id = models.CharField(primary_key=True, max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    contract_type = models.CharField(max_length=30)
    employee_type = models.CharField(max_length=30)
    faculty_code = models.IntegerField()
    campus_code = models.IntegerField()
    birth_place_code = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'employees'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_type})"
