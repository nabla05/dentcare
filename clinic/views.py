from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import models
from datetime import date

from .models import Patient, Employee, Appointment, Diagnosis, ActivityLog, WaitingList, Receptionist, UnavailableDate, Rapport
from .utils import staff_required, admin_required, log_action
from authentication.models import User
from billing.models import Payslip


# ── Dashboard ──────────────────────────────────────────
@staff_required
def dashboard(request):
    total_patients       = Patient.objects.count()
    total_doctors        = Employee.objects.filter(user__role='doctor').count()
    total_receptionists  = Receptionist.objects.count()
    total_appointments   = Appointment.objects.count()
    waiting              = WaitingList.objects.count()
    total_diagnoses      = Diagnosis.objects.count()
    total_payslips       = Payslip.objects.count()
    recent_logs          = ActivityLog.objects.select_related('user')[:8]
    todays_appointments  = Appointment.objects.filter(
        date=date.today()
    ).select_related('patient', 'doctor__user').order_by('start_time')

    return render(request, 'clinic/dashboard.html', {
        'total_patients':      total_patients,
        'total_doctors':       total_doctors,
        'total_receptionists': total_receptionists,
        'total_appointments':  total_appointments,
        'waiting':             waiting,
        'total_diagnoses':     total_diagnoses,
        'total_payslips':      total_payslips,
        'recent_logs':         recent_logs,
        'todays_appointments': todays_appointments,
    })


# ── Patient List ───────────────────────────────────────
@staff_required
def patient_list(request):
    search   = request.GET.get('search', '')
    patients = Patient.objects.all()
    if search:
        patients = patients.filter(
            first_name__icontains=search
        ) | patients.filter(
            last_name__icontains=search
        ) | patients.filter(
            email__icontains=search
        )
    paginator   = Paginator(patients, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'clinic/patients/list.html', {
        'page_obj': page_obj,
        'search':   search,
        'total':    patients.count(),
    })


# ── Add Patient ────────────────────────────────────────
@staff_required
def patient_add(request):
    if request.method == 'POST':
        try:
            patient = Patient.objects.create(
                first_name     = request.POST['first_name'],
                last_name      = request.POST['last_name'],
                email          = request.POST['email'],
                phone          = request.POST['phone'],
                date_of_birth  = request.POST['date_of_birth'],
                gender         = request.POST['gender'],
                blood_group    = request.POST.get('blood_group', ''),
                address        = request.POST.get('address', ''),
                city           = request.POST.get('city', ''),
                country        = request.POST.get('country', 'USA'),
                state_province = request.POST.get('state_province', ''),
                postal_code    = request.POST.get('postal_code', ''),
                allergies      = request.POST.get('allergies', ''),
                medical_notes  = request.POST.get('medical_notes', ''),
                avatar         = request.FILES.get('avatar'),
            )
            log_action(request.user, 'Patient ajouté', patient.get_full_name())
            messages.success(request, "Patient ajouté avec succès !")
            return redirect('clinic:patient_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'clinic/patients/form.html', {'action': 'Add'})


# ── Edit Patient ───────────────────────────────────────
@staff_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        try:
            patient.first_name     = request.POST['first_name']
            patient.last_name      = request.POST['last_name']
            patient.email          = request.POST['email']
            patient.phone          = request.POST['phone']
            patient.date_of_birth  = request.POST['date_of_birth']
            patient.gender         = request.POST['gender']
            patient.blood_group    = request.POST.get('blood_group', '')
            patient.address        = request.POST.get('address', '')
            patient.city           = request.POST.get('city', '')
            patient.country        = request.POST.get('country', 'USA')
            patient.state_province = request.POST.get('state_province', '')
            patient.postal_code    = request.POST.get('postal_code', '')
            patient.allergies      = request.POST.get('allergies', '')
            patient.medical_notes  = request.POST.get('medical_notes', '')
            if request.FILES.get('avatar'):
                patient.avatar = request.FILES['avatar']
            patient.save()
            log_action(request.user, 'Patient mis à jour', patient.get_full_name())
            messages.success(request, "Patient mis à jour avec succès !")
            return redirect('clinic:patient_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'clinic/patients/form.html', {
        'action': 'Edit', 'patient': patient
    })


# ── Delete Patient ─────────────────────────────────────
@staff_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        name = patient.get_full_name()
        patient.delete()
        log_action(request.user, 'Patient supprimé', name)
        messages.success(request, "Patient supprimé avec succès !")
        return redirect('clinic:patient_list')
    return render(request, 'clinic/patients/confirm_delete.html', {'patient': patient})


# ── Bulk Delete Patients ───────────────────────────────
@admin_required
def patient_delete_multiple(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        if not ids:
            messages.warning(request, "Aucun patient sélectionné.")
            return redirect('clinic:patient_list')
        patients = Patient.objects.filter(pk__in=ids)
        count = patients.count()
        for patient in patients:
            log_action(request.user, 'Patient supprimé', patient.get_full_name())
            patient.delete()
        messages.success(request, f'{count} patient(s) deleted successfully.')
    return redirect('clinic:patient_list')


# ── Employee List ──────────────────────────────────────
@admin_required
def employee_list(request):
    search    = request.GET.get('search', '')
    employees = Employee.objects.select_related('user').all()
    if search:
        employees = employees.filter(
            user__first_name__icontains=search
        ) | employees.filter(
            user__last_name__icontains=search
        ) | employees.filter(
            emp_id__icontains=search
        )
    paginator   = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'clinic/employees/list.html', {
        'page_obj': page_obj,
        'search':   search,
        'total':    employees.count(),
    })


# ── Add Employee ───────────────────────────────────────
@admin_required
def employee_add(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken. Please choose another.')
            return render(request, 'clinic/employees/form.html', {'action': 'Add', 'data': request.POST})

        if email and User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" is already registered.')
            return render(request, 'clinic/employees/form.html', {'action': 'Add', 'data': request.POST})

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'clinic/employees/form.html', {'action': 'Add', 'data': request.POST})

        try:
            user = User.objects.create_user(
                username   = username,
                password   = password,
                first_name = request.POST['first_name'],
                last_name  = request.POST['last_name'],
                email      = email,
                phone      = request.POST.get('phone', ''),
                role       = request.POST['role'],
            )
            Employee.objects.create(
                user       = user,
                department = request.POST['department'],
                position   = request.POST['position'],
                salary     = request.POST.get('salary', 0),
                hire_date  = request.POST['hire_date'],
                status     = request.POST.get('status', 'active'),
                notes      = request.POST.get('notes', ''),
            )
            log_action(request.user, 'Added employee', user.get_full_name())
            messages.success(request, "Employé ajouté avec succès !")
            return redirect('clinic:employee_list')
        except Exception as e:
            messages.error(request, f'Unexpected error: {e}')
    return render(request, 'clinic/employees/form.html', {'action': 'Add'})


# ── Edit Employee ──────────────────────────────────────
@admin_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        try:
            u = employee.user
            u.first_name = request.POST['first_name']
            u.last_name  = request.POST['last_name']
            u.email      = request.POST['email']
            u.phone      = request.POST.get('phone', '')
            u.role       = request.POST['role']
            if request.POST.get('password'):
                u.set_password(request.POST['password'])
            u.save()
            employee.department = request.POST['department']
            employee.position   = request.POST['position']
            employee.salary     = request.POST.get('salary', 0)
            employee.hire_date  = request.POST['hire_date']
            employee.status     = request.POST.get('status', 'active')
            employee.notes      = request.POST.get('notes', '')
            employee.save()
            log_action(request.user, 'Updated employee', u.get_full_name())
            messages.success(request, "Employé mis à jour avec succès !")
            return redirect('clinic:employee_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'clinic/employees/form.html', {
        'action': 'Edit', 'employee': employee
    })


# ── Delete Employee ────────────────────────────────────
@admin_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.user.get_full_name()
        employee.user.delete()
        log_action(request.user, 'Deleted employee', name)
        messages.success(request, "Employé supprimé avec succès !")
        return redirect('clinic:employee_list')
    return render(request, 'clinic/employees/confirm_delete.html', {'employee': employee})


# ── Appointment List ───────────────────────────────────
@staff_required
def appointment_list(request):
    appointments       = Appointment.objects.select_related('patient', 'doctor__user').all()
    filter_date        = request.GET.get('date', '')
    filter_doctor      = request.GET.get('doctor', '')
    filter_status      = request.GET.get('status', '')
    filter_apt_id      = request.GET.get('appointment_id', '')
    filter_patient     = request.GET.get('patient_name', '')
    if filter_date:
        appointments = appointments.filter(date=filter_date)
    if filter_doctor:
        appointments = appointments.filter(doctor__id=filter_doctor)
    if filter_status:
        appointments = appointments.filter(status=filter_status)
    if filter_apt_id:
        appointments = appointments.filter(apt_id__icontains=filter_apt_id)
    if filter_patient:
        appointments = appointments.filter(
            patient__first_name__icontains=filter_patient
        ) | appointments.filter(
            patient__last_name__icontains=filter_patient
        ) | appointments.filter(
            patient__user__username__icontains=filter_patient
        )
    paginator   = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    doctors     = Employee.objects.filter(user__role='doctor')
    return render(request, 'clinic/appointments/list.html', {
        'page_obj':      page_obj,
        'doctors':       doctors,
        'filter_date':   filter_date,
        'filter_doctor': filter_doctor,
        'filter_status': filter_status,
        'total':         appointments.count(),
        'statuses':      Appointment.Status.choices,
    })


# ── Add Appointment ────────────────────────────────────
@staff_required
def appointment_add(request):
    patients = Patient.objects.all()
    doctors  = Employee.objects.filter(user__role='doctor')
    if request.method == 'POST':
        patient_id = request.POST['patient']
        doctor_id  = request.POST['doctor']
        appt_date  = request.POST['date']
        start_time = request.POST['start_time']
        end_time   = request.POST['end_time']
        patient = get_object_or_404(Patient, pk=patient_id)
        doctor  = get_object_or_404(Employee, pk=doctor_id)
        errors  = []
        if appt_date < str(date.today()):
            errors.append("Appointment date cannot be in the past.")
        active_count = Appointment.objects.filter(
            patient=patient, date__gte=date.today(),
            status__in=['pending', 'confirmed']
        ).count()
        if active_count >= 3:
            errors.append(f"{patient.get_full_name()} already has 3 active appointments.")
        overlap = Appointment.objects.filter(
            doctor=doctor, date=appt_date,
            status__in=['pending', 'confirmed']
        ).exclude(end_time__lte=start_time).exclude(start_time__gte=end_time)
        if overlap.exists():
            errors.append("This doctor already has an appointment during that time slot.")
        if UnavailableDate.objects.filter(doctor=doctor, date=appt_date).exists():
            errors.append("This doctor is unavailable on the selected date.")
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            Appointment.objects.create(
                patient=patient, doctor=doctor,
                date=appt_date, start_time=start_time, end_time=end_time,
                reason=request.POST.get('reason', ''),
                notes=request.POST.get('notes', ''),
                status=request.POST.get('status', 'pending'),
            )
            log_action(request.user, 'Booked appointment', f'APT for {patient.get_full_name()}')
            messages.success(request, 'Appointment booked successfully!')
            return redirect('clinic:appointment_list')
    return render(request, 'clinic/appointments/form.html', {
        'action': 'Add', 'patients': patients, 'doctors': doctors,
    })


# ── Edit Appointment ───────────────────────────────────
@staff_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    patients    = Patient.objects.all()
    doctors     = Employee.objects.filter(user__role='doctor')
    if request.method == 'POST':
        patient_id = request.POST['patient']
        doctor_id  = request.POST['doctor']
        appt_date  = request.POST['date']
        start_time = request.POST['start_time']
        end_time   = request.POST['end_time']
        patient = get_object_or_404(Patient, pk=patient_id)
        doctor  = get_object_or_404(Employee, pk=doctor_id)
        errors  = []
        if appt_date < str(date.today()):
            errors.append("Appointment date cannot be in the past.")
        overlap = Appointment.objects.filter(
            doctor=doctor, date=appt_date,
            status__in=['pending', 'confirmed']
        ).exclude(pk=pk).exclude(end_time__lte=start_time).exclude(start_time__gte=end_time)
        if overlap.exists():
            errors.append("This doctor already has an appointment during that time slot.")
        if UnavailableDate.objects.filter(doctor=doctor, date=appt_date).exists():
            errors.append("This doctor is unavailable on the selected date.")
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            appointment.patient    = patient
            appointment.doctor     = doctor
            appointment.date       = appt_date
            appointment.start_time = start_time
            appointment.end_time   = end_time
            appointment.reason     = request.POST.get('reason', '')
            appointment.notes      = request.POST.get('notes', '')
            appointment.status     = request.POST.get('status', 'pending')
            appointment.save()
            log_action(request.user, 'Updated appointment', appointment.apt_id)
            messages.success(request, "Rendez-vous mis à jour avec succès !")
            return redirect('clinic:appointment_list')
    return render(request, 'clinic/appointments/form.html', {
        'action': 'Edit', 'appointment': appointment,
        'patients': patients, 'doctors': doctors,
    })


# ── Cancel Appointment → moves to Waiting List ─────────
@staff_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        WaitingList.objects.create(
            appointment_ref = appointment.apt_id,
            patient         = appointment.patient,
            doctor          = appointment.doctor,
            date            = appointment.date,
            time            = appointment.start_time,
            email           = appointment.patient.email,
            phone           = appointment.patient.phone,
            reason          = appointment.reason,
        )
        appointment.status = 'cancelled'
        appointment.save()
        log_action(request.user, 'Cancelled appointment → waiting list', appointment.apt_id)
        messages.success(request, 'Appointment cancelled and added to waiting list.')
        return redirect('clinic:appointment_list')
    return render(request, 'clinic/appointments/confirm_cancel.html', {
        'appointment': appointment
    })


# ── Waiting List ───────────────────────────────────────
@staff_required
def waiting_list(request):
    entries     = WaitingList.objects.select_related('patient', 'doctor__user').all()
    paginator   = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'clinic/waiting_list.html', {
        'page_obj': page_obj,
        'total':    entries.count(),
    })


# ── Restore from Waiting List ──────────────────────────
@staff_required
def waiting_list_restore(request, pk):
    entry = get_object_or_404(WaitingList, pk=pk)
    if request.method == 'POST':
        from datetime import datetime, timedelta
        start = entry.time
        # default end time = start + 30 minutes
        dummy_dt = datetime.combine(entry.date, start) + timedelta(minutes=30)
        end = dummy_dt.time()
        Appointment.objects.create(
            patient    = entry.patient,
            doctor     = entry.doctor,
            date       = entry.date,
            start_time = start,
            end_time   = end,
            reason     = entry.reason,
            status     = 'pending',
        )
        log_action(request.user, 'Restored appointment from waiting list', entry.appointment_ref)
        entry.delete()
        messages.success(request, 'Appointment restored from waiting list.')
    return redirect('clinic:waiting_list')


# ── Delete from Waiting List ───────────────────────────
@staff_required
def waiting_list_delete(request, pk):
    entry = get_object_or_404(WaitingList, pk=pk)
    if request.method == 'POST':
        log_action(request.user, 'Removed entry from waiting list', entry.appointment_ref)
        entry.delete()
        messages.success(request, 'Entry removed from waiting list.')
    return redirect('clinic:waiting_list')


# ── Diagnosis List ─────────────────────────────────────
@staff_required
def diagnosis_list(request):
    search    = request.GET.get('search', '')
    diagnoses = Diagnosis.objects.select_related('patient', 'doctor__user').all()
    if search:
        diagnoses = diagnoses.filter(
            title__icontains=search
        ) | diagnoses.filter(
            patient__first_name__icontains=search
        ) | diagnoses.filter(
            patient__last_name__icontains=search
        )
    paginator   = Paginator(diagnoses, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'clinic/diagnoses/list.html', {
        'page_obj': page_obj, 'search': search, 'total': diagnoses.count(),
    })


# ── Add Diagnosis ──────────────────────────────────────
@staff_required
def diagnosis_add(request):
    patients     = Patient.objects.all()
    doctors      = Employee.objects.filter(user__role='doctor')
    appointments = Appointment.objects.filter(status__in=['confirmed', 'completed'])
    if request.method == 'POST':
        try:
            from .models import DiagnosisPhoto
            diagnosis = Diagnosis(
                patient     = get_object_or_404(Patient, pk=request.POST['patient']),
                doctor      = get_object_or_404(Employee, pk=request.POST['doctor']),
                title       = request.POST['title'],
                description = request.POST['description'],
                tooth_area  = request.POST.get('tooth_area', ''),
                treatment   = request.POST.get('treatment', ''),
                service     = request.POST.get('service', ''),
            )
            apt_id = request.POST.get('appointment')
            if apt_id:
                diagnosis.appointment = get_object_or_404(Appointment, pk=apt_id)
            diagnosis.save()
            for photo in request.FILES.getlist('photos'):
                DiagnosisPhoto.objects.create(diagnosis=diagnosis, image=photo)
            log_action(request.user, 'Added diagnosis',
                       f'{diagnosis.title} for {diagnosis.patient.get_full_name()}')
            messages.success(request, 'Diagnosis saved successfully!')
            return redirect('clinic:diagnosis_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'clinic/diagnoses/form.html', {
        'action': 'Add', 'patients': patients, 'doctors': doctors,
        'appointments': appointments, 'tooth_areas': Diagnosis.ToothArea.choices,
        'services': Diagnosis.Service.choices,
    })


# ── Edit Diagnosis ─────────────────────────────────────
@staff_required
def diagnosis_edit(request, pk):
    diagnosis    = get_object_or_404(Diagnosis, pk=pk)
    patients     = Patient.objects.all()
    doctors      = Employee.objects.filter(user__role='doctor')
    appointments = Appointment.objects.filter(status__in=['confirmed', 'completed'])
    if request.method == 'POST':
        try:
            from .models import DiagnosisPhoto
            diagnosis.patient     = get_object_or_404(Patient, pk=request.POST['patient'])
            diagnosis.doctor      = get_object_or_404(Employee, pk=request.POST['doctor'])
            diagnosis.title       = request.POST['title']
            diagnosis.description = request.POST['description']
            diagnosis.tooth_area  = request.POST.get('tooth_area', '')
            diagnosis.treatment   = request.POST.get('treatment', '')
            diagnosis.service     = request.POST.get('service', '')
            apt_id = request.POST.get('appointment')
            diagnosis.appointment = get_object_or_404(Appointment, pk=apt_id) if apt_id else None
            diagnosis.save()
            for photo in request.FILES.getlist('photos'):
                DiagnosisPhoto.objects.create(diagnosis=diagnosis, image=photo)
            log_action(request.user, 'Updated diagnosis', diagnosis.title)
            messages.success(request, "Diagnostic mis à jour avec succès !")
            return redirect('clinic:diagnosis_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'clinic/diagnoses/form.html', {
        'action': 'Edit', 'diagnosis': diagnosis, 'patients': patients,
        'doctors': doctors, 'appointments': appointments,
        'tooth_areas': Diagnosis.ToothArea.choices,
        'services': Diagnosis.Service.choices,
    })


# ── Diagnosis Detail ───────────────────────────────────
@staff_required
def diagnosis_detail(request, pk):
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    return render(request, 'clinic/diagnoses/detail.html', {'diagnosis': diagnosis})


# ── Delete Diagnosis ───────────────────────────────────
@staff_required
def diagnosis_delete(request, pk):
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    if request.method == 'POST':
        title = diagnosis.title
        diagnosis.delete()
        log_action(request.user, 'Deleted diagnosis', title)
        messages.success(request, 'Diagnosis deleted.')
        return redirect('clinic:diagnosis_list')
    return render(request, 'clinic/diagnoses/confirm_delete.html', {'diagnosis': diagnosis})


# ── Patient Profile ────────────────────────────────────
@staff_required
def patient_profile(request, pk):
    from .models import Payslip as PatientPayslip
    patient      = get_object_or_404(Patient, pk=pk)
    diagnoses    = Diagnosis.objects.filter(patient=patient).select_related('doctor__user').order_by('-created_at')
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user').order_by('-date')
    rapports     = Rapport.objects.filter(patient=patient).order_by('-uploaded_at')
    payslips     = PatientPayslip.objects.filter(patient=patient).order_by('-payment_date')
    return render(request, 'clinic/patients/profile.html', {
        'patient':      patient,
        'diagnoses':    diagnoses,
        'appointments': appointments,
        'rapports':     rapports,
        'payslips':     payslips,
    })


# ── Diagnosis Photos ───────────────────────────────────
@staff_required
def diagnosis_photos(request, pk):
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    photos    = diagnosis.photos.all()
    if request.method == 'POST' and request.FILES.get('photo'):
        from .models import DiagnosisPhoto
        DiagnosisPhoto.objects.create(
            diagnosis = diagnosis,
            image     = request.FILES['photo'],
        )
        log_action(request.user, 'Added photo to diagnosis', diagnosis.title)
        messages.success(request, 'Photo added successfully!')
        return redirect('clinic:diagnosis_photos', pk=pk)
    return render(request, 'clinic/diagnoses/photos.html', {
        'diagnosis': diagnosis,
        'photos':    photos,
    })


# ── Activity Logs ──────────────────────────────────────
@staff_required
def activity_logs(request):
    logs        = ActivityLog.objects.select_related('user').all()
    paginator   = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'clinic/activity_logs.html', {'page_obj': page_obj})


# ── Settings ───────────────────────────────────────────
@admin_required
def settings_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            u = request.user
            u.first_name = request.POST.get('first_name', u.first_name)
            u.last_name  = request.POST.get('last_name', u.last_name)
            u.email      = request.POST.get('email', u.email)
            u.phone      = request.POST.get('phone', u.phone)
            u.save()
            log_action(request.user, 'Updated profile settings')
            messages.success(request, 'Profile updated successfully!')

        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm      = request.POST.get('confirm_password')
            if not request.user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                log_action(request.user, 'Changed password')
                messages.success(request, 'Password changed successfully!')

        return redirect('clinic:settings')

    return render(request, 'clinic/settings.html', {'user': request.user})

# ══════════════════════════════════════════════════════════
#  PATIENT PAYSLIP VIEWS  (spec §4.8 — patient invoices)
# ══════════════════════════════════════════════════════════

from .models import Payslip as PatientPayslip


@staff_required
def patient_payslip_list(request):
    payslips  = PatientPayslip.objects.select_related('patient', 'diagnosis').order_by('-payment_date')
    paginator = Paginator(payslips, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'clinic/payslips/list.html', {
        'page_obj': page_obj,
        'total':    payslips.count(),
    })


@staff_required
def patient_payslip_detail(request, pk):
    payslip = get_object_or_404(PatientPayslip, pk=pk)
    return render(request, 'clinic/payslips/detail.html', {'payslip': payslip})


@staff_required
def patient_payslip_mark_paid(request, pk):
    payslip = get_object_or_404(PatientPayslip, pk=pk)
    if request.method == 'POST':
        payslip.paid = True
        payslip.save()
        log_action(request.user, 'Marked payslip as paid', f'Invoice #{pk}')
        messages.success(request, 'Invoice marked as paid.')
    return redirect('clinic:patient_payslip_detail', pk=pk)


@staff_required
def patient_payslip_delete(request, pk):
    payslip = get_object_or_404(PatientPayslip, pk=pk)
    if request.method == 'POST':
        patient_pk = payslip.patient.pk
        payslip.delete()
        log_action(request.user, 'Deleted invoice', f'Invoice #{pk}')
        messages.success(request, 'Invoice deleted.')
        return redirect('clinic:patient_profile', pk=patient_pk)
    return render(request, 'clinic/payslips/confirm_delete.html', {'payslip': payslip})


@staff_required
def patient_payslip_pdf(request, pk):
    from django.template.loader import get_template
    from django.http import HttpResponse as _HR
    from xhtml2pdf import pisa
    payslip  = get_object_or_404(PatientPayslip, pk=pk)
    template = get_template('clinic/payslips/pdf_template.html')
    html     = template.render({'payslip': payslip})
    response = _HR(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{pk}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return _HR('PDF generation error', status=500)
    return response


# ══════════════════════════════════════════════════════════
#  AVAILABLE TIMES API  (spec §4.5.6)
# ══════════════════════════════════════════════════════════

@staff_required
def available_times(request):
    from datetime import timedelta, datetime as _dt
    date_str  = request.GET.get('date', '')
    doctor_id = request.GET.get('doctor', '')

    slots = []
    cursor = _dt.strptime('08:00', '%H:%M')
    end_of_day = _dt.strptime('17:00', '%H:%M')
    while cursor < end_of_day:
        slots.append(cursor.strftime('%H:%M'))
        cursor += timedelta(minutes=15)

    if not date_str:
        return JsonResponse({'available_times': slots})

    if doctor_id:
        booked = Appointment.objects.filter(
            doctor__id=doctor_id,
            date=date_str,
            status__in=['pending', 'confirmed'],
        ).values_list('start_time', 'end_time')

        def overlaps(slot_str):
            slot_dt  = _dt.strptime(slot_str, '%H:%M')
            slot_end = slot_dt + timedelta(minutes=15)
            for start, end in booked:
                bs = _dt.combine(_dt.today(), start)
                be = _dt.combine(_dt.today(), end)
                if slot_dt < be and slot_end > bs:
                    return True
            return False

        slots = [s for s in slots if not overlaps(s)]

    return JsonResponse({'available_times': slots})


# ══════════════════════════════════════════════════════════
#  TOGGLE APPOINTMENT STATUS  (spec §4.5.7)
# ══════════════════════════════════════════════════════════

@staff_required
def appointment_toggle_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    appointment = get_object_or_404(Appointment, pk=pk)

    if appointment.status in ('pending', 'confirmed'):
        WaitingList.objects.get_or_create(
            appointment_ref=appointment.apt_id,
            defaults=dict(
                patient=appointment.patient,
                doctor=appointment.doctor,
                date=appointment.date,
                time=appointment.start_time,
                email=appointment.patient.email,
                phone=appointment.patient.phone,
                reason=appointment.reason,
            )
        )
        appointment.status = 'cancelled'
        appointment.save()
        log_action(request.user, 'Toggled appointment cancelled', appointment.apt_id)
        return JsonResponse({'status': 'Inactive'})
    else:
        WaitingList.objects.filter(appointment_ref=appointment.apt_id).delete()
        appointment.status = 'pending'
        appointment.save()
        log_action(request.user, 'Toggled appointment restored', appointment.apt_id)
        return JsonResponse({'status': 'Active'})


# ══════════════════════════════════════════════════════════
#  H1 — PATIENT PORTAL  (spec §4.4.9–4.4.13)
# ══════════════════════════════════════════════════════════

from django.contrib.auth.decorators import login_required as _login_required


def _get_patient_or_none(user):
    """Return the Patient linked to this user, or None."""
    try:
        return user.patient_profile
    except Exception:
        return None


@_login_required
def portal_my_appointments(request):
    """GET /my-appointments/ — patient sees their own appointments."""
    patient = _get_patient_or_none(request.user)
    if not patient:
        messages.error(request, "No patient profile linked to your account.")
        return redirect('home:home')
    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related('doctor__user').order_by('-date', '-start_time')
    paginator = Paginator(appointments, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'clinic/portal/my_appointments.html', {
        'page_obj': page_obj,
        'patient':  patient,
    })


@_login_required
def portal_appointment_delete(request, pk):
    """POST /my-appointments/<pk>/delete/ — patient deletes their own appointment."""
    patient = _get_patient_or_none(request.user)
    if not patient:
        return redirect('home:home')
    appointment = get_object_or_404(Appointment, pk=pk, patient=patient)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Rendez-vous annulé.")
    return redirect('clinic:portal_my_appointments')


@_login_required
def portal_appointment_delete_all(request):
    """POST /my-appointments/delete-all/ — patient deletes all their appointments."""
    patient = _get_patient_or_none(request.user)
    if not patient:
        return redirect('home:home')
    if request.method == 'POST':
        Appointment.objects.filter(patient=patient).delete()
        messages.success(request, 'All appointments cancelled.')
    return redirect('clinic:portal_my_appointments')


@_login_required
def portal_book_appointment(request):
    """GET|POST /my-appointments/book/ — logged-in patient books a new appointment."""
    patient = _get_patient_or_none(request.user)
    if not patient:
        messages.error(request, "No patient profile linked to your account.")
        return redirect('home:home')
    doctors = Employee.objects.filter(user__role='doctor', status='active')
    if request.method == 'POST':
        doctor_id  = request.POST.get('doctor', '')
        appt_date  = request.POST.get('date', '')
        start_time = request.POST.get('start_time', '')
        reason     = request.POST.get('reason', '')
        errors = []
        if not all([doctor_id, appt_date, start_time]):
            errors.append("Please fill in all required fields.")
        if appt_date and appt_date < str(date.today()):
            errors.append("Appointment date cannot be in the past.")
        if not errors:
            doctor = get_object_or_404(Employee, pk=doctor_id)
            active_count = Appointment.objects.filter(
                patient=patient, date__gte=date.today(),
                status__in=['pending', 'confirmed']
            ).count()
            if active_count >= 3:
                errors.append("You already have 3 active upcoming appointments.")
            if UnavailableDate.objects.filter(doctor=doctor, date=appt_date).exists():
                errors.append("This doctor is unavailable on the selected date.")
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            from datetime import datetime as _dt, timedelta as _td
            end_dt = _dt.strptime(start_time, '%H:%M') + _td(minutes=30)
            Appointment.objects.create(
                patient=patient, doctor=doctor,
                date=appt_date,
                start_time=start_time,
                end_time=end_dt.strftime('%H:%M'),
                reason=reason,
                status='pending',
            )
            messages.success(request, 'Appointment request submitted successfully!')
            return redirect('clinic:portal_my_appointments')
    return render(request, 'clinic/portal/book_appointment.html', {
        'doctors': doctors,
        'patient': patient,
    })


# ══════════════════════════════════════════════════════════
#  H2 — RAPPORT (PDF REPORT) MODULE  (spec §4.7)
# ══════════════════════════════════════════════════════════

@staff_required
def rapport_add(request, patient_pk):
    """GET|POST /patients/<patient_pk>/rapport/add/"""
    patient = get_object_or_404(Patient, pk=patient_pk)
    if request.method == 'POST' and request.FILES.get('file'):
        Rapport.objects.create(patient=patient, file=request.FILES['file'])
        log_action(request.user, 'Uploaded rapport', patient.get_full_name())
        messages.success(request, 'Rapport uploaded successfully.')
        return redirect('clinic:patient_profile', pk=patient_pk)
    return render(request, 'clinic/rapports/add.html', {'patient': patient})


@staff_required
def rapport_view(request, pk):
    """GET /rapports/<pk>/ — view PDF in iframe."""
    rapport = get_object_or_404(Rapport, pk=pk)
    return render(request, 'clinic/rapports/view.html', {'rapport': rapport})


@staff_required
def rapport_delete(request, pk):
    """POST /rapports/<pk>/delete/"""
    rapport  = get_object_or_404(Rapport, pk=pk)
    patient_pk = rapport.patient.pk
    if request.method == 'POST':
        rapport.delete()
        log_action(request.user, 'Deleted rapport', f'Patient #{patient_pk}')
        messages.success(request, 'Rapport deleted.')
    return redirect('clinic:patient_profile', pk=patient_pk)


# ══════════════════════════════════════════════════════════
#  H5 — GET LATEST EMPLOYEE ID  (spec §4.3.3)
# ══════════════════════════════════════════════════════════

@admin_required
def get_latest_employee_id(request):
    """GET /employees/latest-id/ → {"employee_id": "EMP0005"}"""
    last = Employee.objects.order_by('id').last()
    next_num = (last.id + 1) if last else 1
    return JsonResponse({'employee_id': f'EMP{next_num:04d}'})


# ══════════════════════════════════════════════════════════
#  H6 — MARK UNAVAILABLE DATE  (spec §4.5.8)
# ══════════════════════════════════════════════════════════

@admin_required
def mark_unavailable(request):
    """
    POST /appointments/mark-unavailable/
    body: doctor_id, unavailable_date, action='mark'|'cancel'
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    doctor_id = request.POST.get('doctor_id')
    date_str  = request.POST.get('unavailable_date')
    action    = request.POST.get('action', 'mark')
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'doctor_id and unavailable_date required'}, status=400)
    doctor = get_object_or_404(Employee, pk=doctor_id)
    if action == 'mark':
        _, created = UnavailableDate.objects.get_or_create(doctor=doctor, date=date_str)
        log_action(request.user, 'Marked doctor unavailable', f'{doctor} on {date_str}')
        return JsonResponse({'status': 'marked', 'created': created})
    elif action == 'cancel':
        deleted, _ = UnavailableDate.objects.filter(doctor=doctor, date=date_str).delete()
        log_action(request.user, 'Cancelled unavailable date', f'{doctor} on {date_str}')
        return JsonResponse({'status': 'cancelled', 'deleted': deleted})
    return JsonResponse({'error': 'action must be mark or cancel'}, status=400)


# ══════════════════════════════════════════════════════════
#  M6 — BULK DELETE APPOINTMENTS  (spec §4.5.5)
# ══════════════════════════════════════════════════════════

@staff_required
def appointment_delete_multiple(request):
    """POST /appointments/delete-multiple/ — delete a list of appointment IDs."""
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        if not ids:
            messages.warning(request, "Aucun rendez-vous sélectionné.")
            return redirect('clinic:appointment_list')
        appointments = Appointment.objects.filter(pk__in=ids)
        count = appointments.count()
        for appt in appointments:
            log_action(request.user, 'Deleted appointment',
                       f'{appt.apt_id} — {appt.patient.get_full_name()} on {appt.date}')
        appointments.delete()
        messages.success(request, f'{count} appointment(s) deleted.')
    return redirect('clinic:appointment_list')


# ══════════════════════════════════════════════════════════
#  LOW-1 — GLOBAL SEARCH  (spec §8.6 #17)
# ══════════════════════════════════════════════════════════

@staff_required
def global_search(request):
    """GET /search/?q=… — unified search across patients, appointments, employees."""
    q = request.GET.get('q', '').strip()
    results = {'patients': [], 'appointments': [], 'employees': []}
    if len(q) >= 2:
        results['patients'] = Patient.objects.filter(
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q)  |
            models.Q(email__icontains=q)       |
            models.Q(phone__icontains=q)
        )[:10]
        results['appointments'] = Appointment.objects.filter(
            models.Q(apt_id__icontains=q) |
            models.Q(patient__first_name__icontains=q) |
            models.Q(patient__last_name__icontains=q)
        ).select_related('patient', 'doctor__user')[:10]
        results['employees'] = Employee.objects.filter(
            models.Q(emp_id__icontains=q) |
            models.Q(user__first_name__icontains=q) |
            models.Q(user__last_name__icontains=q)  |
            models.Q(user__email__icontains=q)
        ).select_related('user')[:10]
    total = (len(results['patients']) +
             len(results['appointments']) +
             len(results['employees']))
    return render(request, 'clinic/search_results.html', {
        'q': q, 'results': results, 'total': total
    })


# ══════════════════════════════════════════════════════════
#  LOW-2 — ANALYTICS  (spec §8.6 #18)
# ══════════════════════════════════════════════════════════

@staff_required
def analytics(request):
    """GET /analytics/ — charts: appointments/month, revenue/service, popular services."""
    from django.db.models.functions import TruncMonth
    from django.db.models import Count, Sum
    import json

    # Appointments per month (last 12 months)
    appt_by_month = (
        Appointment.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    appt_labels  = [r['month'].strftime('%b %Y') for r in appt_by_month if r['month']]
    appt_data    = [r['count'] for r in appt_by_month if r['month']]

    # Revenue by service
    from .models import Payslip as PatientPayslip
    revenue_by_service = (
        PatientPayslip.objects
        .values('service')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    rev_labels = [r['service'] for r in revenue_by_service]
    rev_data   = [float(r['total']) for r in revenue_by_service]
    rev_counts = [r['count'] for r in revenue_by_service]

    # Summary KPIs
    total_revenue   = sum(rev_data)
    paid_revenue    = float(PatientPayslip.objects.filter(paid=True).aggregate(s=Sum('amount'))['s'] or 0)
    unpaid_revenue  = total_revenue - paid_revenue
    top_service     = rev_labels[0] if rev_labels else '—'

    return render(request, 'clinic/analytics.html', {
        'appt_labels':      json.dumps(appt_labels),
        'appt_data':        json.dumps(appt_data),
        'rev_labels':       json.dumps(rev_labels),
        'rev_data':         json.dumps(rev_data),
        'rev_counts':       json.dumps(rev_counts),
        'total_revenue':    total_revenue,
        'paid_revenue':     paid_revenue,
        'unpaid_revenue':   unpaid_revenue,
        'top_service':      top_service,
        'total_invoices':   PatientPayslip.objects.count(),
        'paid_invoices':    PatientPayslip.objects.filter(paid=True).count(),
    })


# ══════════════════════════════════════════════════════════
#  LOW-4 — REST API  (spec §8.6 #20)
# ══════════════════════════════════════════════════════════

from django.views.decorators.http import require_GET

@staff_required
@require_GET
def api_patients(request):
    """GET /api/patients/ — list patients as JSON."""
    qs = Patient.objects.all().order_by('-created_at')[:50]
    data = [{'id': p.pk, 'name': p.get_full_name(),
             'email': p.email, 'phone': p.phone,
             'city': p.city, 'status': p.status} for p in qs]
    return JsonResponse({'count': len(data), 'patients': data})


@staff_required
@require_GET
def api_patient_detail(request, pk):
    """GET /api/patients/<pk>/ — single patient with appointments."""
    p = get_object_or_404(Patient, pk=pk)
    appointments = list(Appointment.objects.filter(patient=p).values(
        'pk', 'apt_id', 'date', 'start_time', 'status'
    ))
    for a in appointments:
        a['date'] = str(a['date'])
        a['start_time'] = str(a['start_time'])
    return JsonResponse({
        'id': p.pk, 'first_name': p.first_name, 'last_name': p.last_name,
        'email': p.email, 'phone': p.phone, 'city': p.city,
        'country': p.country, 'date_of_birth': str(p.date_of_birth),
        'gender': p.gender, 'blood_group': p.blood_group,
        'appointments': appointments,
    })


@staff_required
@require_GET
def api_appointments(request):
    """GET /api/appointments/?date=YYYY-MM-DD&status=pending"""
    qs = Appointment.objects.select_related('patient', 'doctor__user').all()
    if request.GET.get('date'):
        qs = qs.filter(date=request.GET['date'])
    if request.GET.get('status'):
        qs = qs.filter(status=request.GET['status'])
    qs = qs.order_by('-date', '-start_time')[:100]
    data = [{
        'id': a.pk, 'apt_id': a.apt_id,
        'patient': a.patient.get_full_name() if a.patient else None,
        'doctor': a.doctor.user.get_full_name() if a.doctor else None,
        'date': str(a.date), 'time': str(a.start_time),
        'status': a.status,
    } for a in qs]
    return JsonResponse({'count': len(data), 'appointments': data})


@staff_required
@require_GET
def api_employees(request):
    """GET /api/employees/ — list all employees."""
    qs = Employee.objects.select_related('user').all()
    data = [{
        'id': e.pk, 'emp_id': e.emp_id,
        'name': e.user.get_full_name(),
        'email': e.user.email, 'phone': e.phone,
        'role': e.role, 'status': e.status,
    } for e in qs]
    return JsonResponse({'count': len(data), 'employees': data})


@staff_required
@require_GET
def api_dashboard_stats(request):
    """GET /api/stats/ — dashboard KPIs as JSON."""
    from .models import Payslip as PatientPayslip
    from django.db.models import Sum
    return JsonResponse({
        'total_patients':      Patient.objects.count(),
        'total_doctors':       Employee.objects.filter(user__role='doctor').count(),
        'total_receptionists': Receptionist.objects.count(),
        'total_appointments':  Appointment.objects.count(),
        'waiting_list':        WaitingList.objects.count(),
        'total_diagnoses':     Diagnosis.objects.count(),
        'total_invoices':      PatientPayslip.objects.count(),
        'total_revenue':       float(PatientPayslip.objects.aggregate(s=Sum('amount'))['s'] or 0),
        'paid_revenue':        float(PatientPayslip.objects.filter(paid=True).aggregate(s=Sum('amount'))['s'] or 0),
    })
