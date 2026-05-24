from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('dashboard/',                            views.dashboard,              name='dashboard'),

    # Patients
    path('patients/',                             views.patient_list,           name='patient_list'),
    path('patients/add/',                         views.patient_add,            name='patient_add'),
    path('patients/<int:pk>/edit/',               views.patient_edit,           name='patient_edit'),
    path('patients/<int:pk>/delete/',             views.patient_delete,         name='patient_delete'),
    path('patients/delete-multiple/',             views.patient_delete_multiple, name='patient_delete_multiple'),

    # Employees
    path('employees/',                            views.employee_list,          name='employee_list'),
    path('employees/add/',                        views.employee_add,           name='employee_add'),
    path('employees/<int:pk>/edit/',              views.employee_edit,          name='employee_edit'),
    path('employees/<int:pk>/delete/',            views.employee_delete,        name='employee_delete'),

    # Appointments
    path('appointments/',                         views.appointment_list,       name='appointment_list'),
    path('appointments/add/',                     views.appointment_add,        name='appointment_add'),
    path('appointments/<int:pk>/edit/',           views.appointment_edit,       name='appointment_edit'),
    path('appointments/<int:pk>/cancel/',         views.appointment_cancel,     name='appointment_cancel'),

    # Waiting List
    path('waiting-list/',                         views.waiting_list,           name='waiting_list'),
    path('waiting-list/<int:pk>/restore/',        views.waiting_list_restore,   name='waiting_list_restore'),
    path('waiting-list/<int:pk>/delete/',         views.waiting_list_delete,    name='waiting_list_delete'),

    # Patient Profile
    path('patients/<int:pk>/profile/',            views.patient_profile,        name='patient_profile'),

    # Diagnoses
    path('diagnoses/',                            views.diagnosis_list,         name='diagnosis_list'),
    path('diagnoses/add/',                        views.diagnosis_add,          name='diagnosis_add'),
    path('diagnoses/<int:pk>/',                   views.diagnosis_detail,       name='diagnosis_detail'),
    path('diagnoses/<int:pk>/edit/',              views.diagnosis_edit,         name='diagnosis_edit'),
    path('diagnoses/<int:pk>/delete/',            views.diagnosis_delete,       name='diagnosis_delete'),
    path('diagnoses/<int:pk>/photos/',            views.diagnosis_photos,       name='diagnosis_photos'),

    # Activity Logs
    path('activity-logs/',                        views.activity_logs,          name='activity_logs'),

    # Settings
    path('settings/',                             views.settings_view,          name='settings'),

    # Patient Payslips / Invoices  (spec §4.8)
    path('invoices/',                             views.patient_payslip_list,        name='patient_payslip_list'),
    path('invoices/<int:pk>/',                    views.patient_payslip_detail,      name='patient_payslip_detail'),
    path('invoices/<int:pk>/mark-paid/',          views.patient_payslip_mark_paid,   name='patient_payslip_mark_paid'),
    path('invoices/<int:pk>/delete/',             views.patient_payslip_delete,      name='patient_payslip_delete'),
    path('invoices/<int:pk>/pdf/',                views.patient_payslip_pdf,         name='patient_payslip_pdf'),

    # Available times AJAX  (spec §4.5.6)
    path('appointments/available-times/',         views.available_times,             name='available_times'),

    # Toggle appointment status  (spec §4.5.7)
    path('appointments/<int:pk>/toggle-status/',  views.appointment_toggle_status,   name='appointment_toggle_status'),

    # H6 - Mark unavailable date  (spec §4.5.8)
    path('appointments/mark-unavailable/',        views.mark_unavailable,            name='mark_unavailable'),

    # H5 - Latest employee ID  (spec §4.3.3)
    path('employees/latest-id/',                  views.get_latest_employee_id,      name='get_latest_employee_id'),

    # H2 - Rapport module  (spec §4.7)
    path('patients/<int:patient_pk>/rapport/add/', views.rapport_add,                name='rapport_add'),
    path('rapports/<int:pk>/',                     views.rapport_view,               name='rapport_view'),
    path('rapports/<int:pk>/delete/',              views.rapport_delete,             name='rapport_delete'),

    # H1 - Patient portal  (spec §4.4.9-4.4.13)
    path('my-appointments/',                       views.portal_my_appointments,        name='portal_my_appointments'),
    path('my-appointments/book/',                  views.portal_book_appointment,       name='portal_book_appointment'),
    path('my-appointments/<int:pk>/delete/',       views.portal_appointment_delete,     name='portal_appointment_delete'),
    path('my-appointments/delete-all/',            views.portal_appointment_delete_all, name='portal_appointment_delete_all'),

    # M6 - Bulk delete appointments  (spec §4.5.5)
    path('appointments/delete-multiple/',          views.appointment_delete_multiple,   name='appointment_delete_multiple'),

    # LOW-1 — Global search
    path('search/',                                views.global_search,           name='global_search'),

    # LOW-2 — Analytics
    path('analytics/',                             views.analytics,               name='analytics'),

    # LOW-4 — REST API
    path('api/patients/',                          views.api_patients,            name='api_patients'),
    path('api/patients/<int:pk>/',                 views.api_patient_detail,      name='api_patient_detail'),
    path('api/appointments/',                      views.api_appointments,        name='api_appointments'),
    path('api/employees/',                         views.api_employees,           name='api_employees'),
    path('api/stats/',                             views.api_dashboard_stats,     name='api_dashboard_stats'),
]