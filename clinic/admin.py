from django.contrib import admin
from .models import Patient
from .models import Patient, Employee
from .models import Patient, Employee, Appointment
from .models import Patient, Employee, Appointment, Diagnosis

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'phone', 'gender', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['emp_id', 'user', 'department', 'position', 'status']
    list_filter  = ['department', 'status']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['apt_id', 'patient', 'doctor', 'date', 'start_time', 'status']
    list_filter  = ['status', 'date']

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'doctor', 'tooth_area', 'created_at']
    list_filter  = ['tooth_area']