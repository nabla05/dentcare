import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import User


class Patient(models.Model):

    class Gender(models.TextChoices):
        MALE   = 'male',   'Male'
        FEMALE = 'female', 'Female'
        OTHER  = 'other',  'Other'

    class BloodGroup(models.TextChoices):
        A_POS  = 'A+',  'A+'
        A_NEG  = 'A-',  'A-'
        B_POS  = 'B+',  'B+'
        B_NEG  = 'B-',  'B-'
        O_POS  = 'O+',  'O+'
        O_NEG  = 'O-',  'O-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'

    user          = models.OneToOneField(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='patient_profile'
    )
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    email         = models.EmailField(unique=True)
    phone         = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender        = models.CharField(max_length=10, choices=Gender.choices)
    blood_group   = models.CharField(max_length=5, choices=BloodGroup.choices, blank=True)
    address       = models.TextField(blank=True)
    city          = models.CharField(max_length=100, blank=True)
    country       = models.CharField(max_length=100, blank=True, default='USA')
    state_province = models.CharField(max_length=100, blank=True, default='California')
    postal_code   = models.CharField(max_length=20, blank=True)
    avatar        = models.ImageField(upload_to='avatars/', blank=True, null=True)
    allergies     = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Employee(models.Model):

    class Department(models.TextChoices):
        DENTISTRY    = 'dentistry',    'Dentistry'
        ORTHODONTICS = 'orthodontics', 'Orthodontics'
        RECEPTION    = 'reception',    'Reception'
        ADMIN        = 'admin',        'Admin'

    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Active'
        INACTIVE = 'inactive', 'Inactive'

    emp_id     = models.CharField(max_length=10, unique=True, editable=False)
    user       = models.OneToOneField(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    department = models.CharField(max_length=20, choices=Department.choices)
    position   = models.CharField(max_length=100)
    salary     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hire_date  = models.DateField()
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['emp_id']

    def __str__(self):
        return f"{self.emp_id} — {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.emp_id:
            last = Employee.objects.order_by('id').last()
            next_num = (last.id + 1) if last else 1
            self.emp_id = f"EMP{next_num:04d}"
        super().save(*args, **kwargs)


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    apt_id = models.CharField(max_length=10, unique=True, editable=False)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='appointments'
    )
    doctor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='appointments',
        limit_choices_to={'user__role': 'doctor'}
    )
    date       = models.DateField()
    start_time = models.TimeField()
    end_time   = models.TimeField()
    reason     = models.CharField(max_length=255, blank=True)
    notes      = models.TextField(blank=True)
    email      = models.EmailField(blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.apt_id} — {self.patient} with Dr.{self.doctor.user.last_name}"

    def save(self, *args, **kwargs):
        if not self.apt_id:
            last = Appointment.objects.order_by('id').last()
            next_num = (last.id + 1) if last else 1
            self.apt_id = f"APT{next_num:04d}"
        super().save(*args, **kwargs)


class Diagnosis(models.Model):

    class ToothArea(models.TextChoices):
        UPPER_LEFT  = 'upper_left',  'Upper Left'
        UPPER_RIGHT = 'upper_right', 'Upper Right'
        LOWER_LEFT  = 'lower_left',  'Lower Left'
        LOWER_RIGHT = 'lower_right', 'Lower Right'
        FULL_MOUTH  = 'full_mouth',  'Full Mouth'

    class Service(models.TextChoices):
        TEETH_WHITENING  = 'Teeth Whitening',  'Teeth Whitening'
        TEETH_CLEANING   = 'Teeth Cleaning',   'Teeth Cleaning'
        QUALITY_BRACKETS = 'Quality Brackets', 'Quality Brackets'
        MODERN_ANESTHETIC = 'Modern Anesthetic', 'Modern Anesthetic'
        DENTAL_CALCULUS  = 'Dental Calculus',  'Dental Calculus'
        PARADONTOSIS     = 'Paradontosis',     'Paradontosis'
        DENTAL_IMPLANTS  = 'Dental Implants',  'Dental Implants'
        TOOTH_BRACES     = 'Tooth Braces',     'Tooth Braces'

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='diagnoses'
    )
    doctor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='diagnoses',
        limit_choices_to={'user__role': 'doctor'}
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='diagnoses'
    )
    title       = models.CharField(max_length=200)
    description = models.TextField()
    tooth_area  = models.CharField(max_length=20, choices=ToothArea.choices, blank=True)
    treatment   = models.TextField(blank=True)
    service     = models.CharField(
        max_length=50, choices=Service.choices, blank=True
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Diagnoses'

    def __str__(self):
        return f"{self.title} — {self.patient.get_full_name()}"


class ActivityLog(models.Model):
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    action     = models.CharField(max_length=255)
    details    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def timestamp(self):
        return self.created_at

    def __str__(self):
        return f"{self.user} — {self.action}"


class WaitingList(models.Model):

    class Status(models.TextChoices):
        WAITING   = 'waiting',   'Waiting'
        SCHEDULED = 'scheduled', 'Scheduled'

    appointment_ref = models.CharField(max_length=10, blank=True)
    patient  = models.ForeignKey(
        Patient, on_delete=models.SET_NULL, null=True, related_name='waiting_entries'
    )
    doctor   = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, related_name='waiting_entries'
    )
    date     = models.DateField()
    time     = models.TimeField()
    email    = models.EmailField(blank=True)
    phone    = models.CharField(max_length=20, blank=True)
    reason   = models.TextField(blank=True)
    status   = models.CharField(max_length=12, choices=Status.choices, default=Status.WAITING)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"Waiting: {self.patient} — {self.date}"


# ── #1 Rapport ────────────────────────────────────────────────────────────────

class Rapport(models.Model):
    patient     = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='rapports'
    )
    file        = models.FileField(upload_to='rapports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Rapport — {self.patient}"

    def save(self, *args, **kwargs):
        # Rename to {username}_rapport.pdf before the first save
        if self.file and hasattr(self.patient, 'user'):
            username = self.patient.user.username if hasattr(self.patient, 'user') and self.patient.user_id else 'unknown'
            ext = os.path.splitext(self.file.name)[1] or '.pdf'
            self.file.name = f"rapports/{username}_rapport{ext}"
        super().save(*args, **kwargs)


# ── #2 Receptionist ───────────────────────────────────────────────────────────

class Receptionist(models.Model):
    user = models.OneToOneField(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='receptionist_profile'
    )

    def __str__(self):
        return f"Receptionist — {self.user.get_full_name()}"


# ── #3 MedicalRecord ──────────────────────────────────────────────────────────

class MedicalRecord(models.Model):
    patient           = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='medical_records'
    )
    receptionist      = models.ForeignKey(
        Receptionist, on_delete=models.CASCADE, related_name='medical_records'
    )
    creation_date     = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    additional_info   = models.TextField(blank=True)

    def __str__(self):
        return f"MedicalRecord #{self.pk} — {self.patient}"


# ── #4 MaintenanceMode (singleton) ────────────────────────────────────────────

class MaintenanceMode(models.Model):
    # id is always 1 — enforced by get_or_create(id=1)
    enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Maintenance Mode'

    def __str__(self):
        return f"Maintenance {'ON' if self.enabled else 'OFF'}"


# ── #5 DiagnosisPhoto (replaces single image field on Diagnosis) ──────────────

class DiagnosisPhoto(models.Model):
    diagnosis = models.ForeignKey(
        Diagnosis, on_delete=models.CASCADE, related_name='photos'
    )
    image     = models.ImageField(upload_to='diagnosis_photos/')

    def __str__(self):
        return f"Photo for {self.diagnosis}"


# ── #6 Payslip (patient invoice, auto-created on Diagnosis save) ───────────────

SERVICE_PRICES = {
    'Teeth Whitening':   100,
    'Teeth Cleaning':     75,
    'Quality Brackets':  200,
    'Modern Anesthetic':  50,
    'Dental Calculus':    80,
    'Paradontosis':       120,
    'Dental Implants':    150,
    'Tooth Braces':       180,
}


class Payslip(models.Model):
    patient      = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='payslips'
    )
    diagnosis    = models.OneToOneField(
        Diagnosis, on_delete=models.CASCADE, related_name='payslip'
    )
    service      = models.CharField(max_length=50, choices=Diagnosis.Service.choices)
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    paid         = models.BooleanField(default=False)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Invoice #{self.pk} — {self.patient} — {self.service}"


@receiver(post_save, sender=Diagnosis)
def create_payslip_for_diagnosis(sender, instance, created, **kwargs):
    if created and instance.service:
        price = SERVICE_PRICES.get(instance.service, 0)
        Payslip.objects.create(
            patient=instance.patient,
            diagnosis=instance,
            service=instance.service,
            amount=price,
        )


# ── #7 UnavailableDate ────────────────────────────────────────────────────────

class UnavailableDate(models.Model):
    doctor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='unavailable_dates'
    )
    date   = models.DateField()

    class Meta:
        unique_together = ('doctor', 'date')

    def __str__(self):
        return f"{self.doctor} unavailable on {self.date}"