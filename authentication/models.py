from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model — extends Django's built-in user.
    We add a 'role' field to control permissions across the system.
    """

    class Role(models.TextChoices):
        ADMIN        = 'admin',        'Admin'
        DOCTOR       = 'doctor',       'Doctor'
        RECEPTIONIST = 'receptionist', 'Receptionist'
        PATIENT      = 'patient',      'Patient'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )

    # Extra profile fields
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    # ── Handy role-check properties ──────────────────
    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT