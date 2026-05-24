from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('payslips/',                   views.payslip_list,   name='payslip_list'),
    path('payslips/add/',               views.payslip_add,    name='payslip_add'),
    path('payslips/<int:pk>/edit/',     views.payslip_edit,   name='payslip_edit'),
    path('payslips/<int:pk>/delete/',   views.payslip_delete, name='payslip_delete'),
    path('payslips/<int:pk>/pdf/',      views.payslip_pdf,    name='payslip_pdf'),
]