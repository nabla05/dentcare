from django.contrib import admin
from .models import Payslip


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'net_salary', 'status']
    list_filter  = ['status', 'month', 'year']