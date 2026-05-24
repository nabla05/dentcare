from django.db import models
from clinic.models import Employee


class Payslip(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID    = 'paid',    'Paid'

    class Month(models.TextChoices):
        JANUARY   = 'January',   'January'
        FEBRUARY  = 'February',  'February'
        MARCH     = 'March',     'March'
        APRIL     = 'April',     'April'
        MAY       = 'May',       'May'
        JUNE      = 'June',      'June'
        JULY      = 'July',      'July'
        AUGUST    = 'August',    'August'
        SEPTEMBER = 'September', 'September'
        OCTOBER   = 'October',   'October'
        NOVEMBER  = 'November',  'November'
        DECEMBER  = 'December',  'December'

    # ── Relations ──────────────────────────────────
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='payslips'
    )

    # ── Period ─────────────────────────────────────
    month = models.CharField(max_length=15, choices=Month.choices)
    year  = models.PositiveIntegerField()

    # ── Salary Components ──────────────────────────
    base_salary  = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary   = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    # ── Status & Notes ─────────────────────────────
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-created_at']

    def __str__(self):
        return f"{self.employee.emp_id} — {self.month} {self.year}"

    def save(self, *args, **kwargs):
        # Auto-calculate net salary
        self.net_salary = self.base_salary + self.bonuses - self.deductions
        super().save(*args, **kwargs)