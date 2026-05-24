# 🦷 DentCare — Dental Practice Management System

> Django-based web application for managing patients, appointments, diagnoses, invoices, and staff in a dental clinic.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Configuration (.env)](#configuration)
5. [Running Migrations](#running-migrations)
6. [Creating a Superuser](#creating-a-superuser)
7. [Loading Test Data](#loading-test-data)
8. [User Roles](#user-roles)
9. [URL Reference](#url-reference)
10. [REST API](#rest-api)
11. [Production Checklist](#production-checklist)
12. [Troubleshooting](#troubleshooting)

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.10+ |
| Django | 4.2.x |
| Pillow | 10.0+ |
| xhtml2pdf | 0.2.11+ |
| python-dotenv | 1.0+ |

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## Quick Start

```bash
# 1. Clone / extract the project
cd dentcare/

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum (see Configuration below)

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (admin account)
python manage.py createsuperuser

# 7. Create the static directory (avoids a startup warning)
mkdir -p static

# 8. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.  
The Django admin panel is at **http://127.0.0.1:8000/admin/**.

---

## Project Structure

```
dentcare/
├── authentication/        # Custom User model, login, register, logout
│   ├── models.py          # User (role: admin | doctor | receptionist | patient)
│   ├── views.py           # login_view, register_view, logout_view
│   └── urls.py            # /auth/login/  /auth/register/  /auth/logout/
│
├── clinic/                # Core app — all dashboard logic
│   ├── models.py          # Patient, Employee, Appointment, Diagnosis,
│   │                      # DiagnosisPhoto, Payslip, Rapport, WaitingList,
│   │                      # Receptionist, UnavailableDate, ActivityLog,
│   │                      # MaintenanceMode, MedicalRecord
│   ├── views.py           # All dashboard, portal, API and search views
│   ├── urls.py            # All clinic URL patterns
│   ├── middleware.py      # RateLimit, MaintenanceMode, PDF, SecurityHeaders
│   └── utils.py           # @staff_required, @admin_required, log_action()
│
├── billing/               # Employee payslips (salary slips)
│   ├── models.py          # Payslip (base + bonus - deductions = net)
│   └── views.py           # List, detail, PDF generation
│
├── home/                  # Public-facing pages
│   └── views.py           # Home, about, services, doctors, blog, contact
│
├── core/
│   ├── settings.py        # All Django settings (reads from .env)
│   └── urls.py            # Root URL config
│
├── templates/             # All HTML templates
│   ├── clinic/            # Dashboard templates
│   │   ├── base.html      # Sidebar layout, global search, mobile responsive
│   │   ├── dashboard.html
│   │   ├── analytics.html # Charts: appointments/month, revenue/service
│   │   ├── search_results.html
│   │   ├── patients/
│   │   ├── appointments/
│   │   ├── diagnoses/
│   │   ├── payslips/
│   │   ├── rapports/
│   │   ├── employees/
│   │   └── portal/        # Patient self-service portal
│   └── authentication/    # Login, register pages
│
├── media/                 # Uploaded files (created automatically)
│   ├── avatars/           # Patient profile photos
│   ├── diagnosis_photos/  # Diagnosis images
│   └── rapports/          # Medical PDF reports
│
├── logs/                  # Application logs (created automatically)
│   ├── dentcare.log
│   └── errors.log
│
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Configuration

Create a `.env` file in the project root (same folder as `manage.py`):

```env
# ── Security ───────────────────────────────────────────────
# REQUIRED: generate a new key for every deployment
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your-secret-key-here

# Set to False in production
DEBUG=True

# ── Database ───────────────────────────────────────────────
# Default: SQLite (fine for development)
# For production use PostgreSQL:
# DATABASE_URL=postgres://user:password@localhost:5432/dentcare

# ── Email ──────────────────────────────────────────────────
# Development default: prints emails to the console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Production SMTP example (Gmail):
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=your@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=noreply@dentcare.com
```

`.env.example` is already included in the project — copy it to `.env` and fill in values.

---

## Running Migrations

```bash
# Apply all migrations (creates the database schema)
python manage.py migrate

# If you added the email/phone fields to Appointment manually,
# the migration file is already included:
#   clinic/migrations/0004_m3_appointment_email_phone.py
# It will run automatically with the command above.
```

To inspect the current migration state:

```bash
python manage.py showmigrations
```

---

## Creating a Superuser

```bash
python manage.py createsuperuser
```

This creates an admin-role user. After logging in at `/auth/login/` you will be redirected to `/dashboard/`.

To create staff accounts (doctors, receptionists) use the **Employees** section of the dashboard.

---

## Loading Test Data

```bash
python manage.py loaddata fixtures/test_data.json
```

If no fixture exists yet, create some initial data through the admin panel at `/admin/` or by using the dashboard's Add Patient / Add Employee forms.

---

## User Roles

| Role | Login redirects to | Access |
|---|---|---|
| `admin` | `/dashboard/` | Everything — full dashboard + Django admin |
| `doctor` | `/dashboard/` | Full dashboard (patients, appointments, diagnoses) |
| `receptionist` | `/dashboard/` | Appointments, waiting list, activity log |
| `patient` | `/` | Patient portal only (`/my-appointments/`) |
| Visitor (no account) | — | Public pages only |

Roles are set on the `User` model's `role` field. Staff accounts are created via the Employees section; patient accounts are created via `/register/` or by staff via Patients → Add Patient.

---

## URL Reference

### Public

| Method | URL | Description |
|---|---|---|
| GET | `/` | Homepage |
| GET | `/about/` | About page |
| GET | `/services/` | Services listing |
| GET | `/doctors/` | Doctor team |
| GET | `/blog/` | Blog |
| GET | `/contact/` | Contact |
| GET/POST | `/login/` | Login (alias → `/auth/login/`) |
| GET/POST | `/register/` | Patient registration |
| GET | `/logout/` | Logout |

### Dashboard — Staff

| Method | URL | Description |
|---|---|---|
| GET | `/dashboard/` | Dashboard home (stats + today's appointments) |
| GET | `/analytics/` | Charts: appointments/month, revenue/service |
| GET | `/search/?q=` | Global search (patients, appointments, employees) |
| GET | `/patients/` | Patient list (search + bulk delete) |
| GET/POST | `/patients/add/` | Add patient |
| GET/POST | `/patients/<pk>/edit/` | Edit patient |
| GET/POST | `/patients/<pk>/delete/` | Delete patient (confirmation page) |
| POST | `/patients/delete-multiple/` | Bulk delete patients |
| GET | `/patients/<pk>/profile/` | Patient profile (tabbed: appointments/diagnoses/invoices/rapports) |
| GET | `/employees/` | Employee list |
| GET/POST | `/employees/add/` | Add employee |
| GET/POST | `/employees/<pk>/edit/` | Edit employee |
| POST | `/employees/<pk>/delete/` | Delete employee |
| GET | `/employees/latest-id/` | JSON: next employee ID (AJAX) |
| GET | `/appointments/` | Appointment list (filters + bulk delete) |
| GET/POST | `/appointments/add/` | Book appointment |
| GET/POST | `/appointments/<pk>/edit/` | Edit appointment |
| POST | `/appointments/<pk>/toggle-status/` | Toggle Active ↔ Cancelled (moves to waiting list) |
| POST | `/appointments/delete-multiple/` | Bulk delete appointments |
| GET | `/appointments/available-times/?date=&doctor=` | JSON: free 15-min slots |
| POST | `/appointments/mark-unavailable/` | Block/unblock a doctor's date |
| GET | `/waiting-list/` | Waiting list |
| GET | `/diagnoses/` | All diagnoses |
| GET/POST | `/diagnoses/add/` | Add diagnosis (auto-creates invoice) |
| GET | `/diagnoses/<pk>/` | Diagnosis detail |
| GET/POST | `/diagnoses/<pk>/edit/` | Edit diagnosis |
| POST | `/diagnoses/<pk>/delete/` | Delete diagnosis |
| GET | `/diagnoses/<pk>/photos/` | Diagnosis photo gallery |
| GET/POST | `/patients/<pk>/rapport/add/` | Upload medical PDF report |
| GET | `/rapports/<pk>/` | View rapport (iframe) |
| POST | `/rapports/<pk>/delete/` | Delete rapport |
| GET | `/invoices/` | Patient invoice list |
| GET | `/invoices/<pk>/` | Invoice detail |
| POST | `/invoices/<pk>/mark-paid/` | Mark invoice as paid |
| GET | `/invoices/<pk>/pdf/` | Download invoice PDF |
| POST | `/invoices/<pk>/delete/` | Delete invoice |
| GET | `/activity-logs/` | Staff activity log |
| GET/POST | `/settings/` | Maintenance mode + doctor unavailability |

### Patient Portal

| Method | URL | Description |
|---|---|---|
| GET | `/my-appointments/` | My appointments list |
| GET/POST | `/my-appointments/book/` | Book an appointment |
| POST | `/my-appointments/<pk>/delete/` | Cancel one appointment |
| POST | `/my-appointments/delete-all/` | Cancel all appointments |

---

## REST API

All endpoints require staff authentication (session cookie or future token auth).  
All responses are `application/json`.

### `GET /api/stats/`
Dashboard KPIs.
```json
{
  "total_patients": 42,
  "total_doctors": 5,
  "total_receptionists": 2,
  "total_appointments": 128,
  "waiting_list": 3,
  "total_diagnoses": 95,
  "total_invoices": 95,
  "total_revenue": 9800.0,
  "paid_revenue": 7200.0
}
```

### `GET /api/patients/`
Returns up to 50 most recent patients.
```json
{
  "count": 42,
  "patients": [
    { "id": 1, "name": "Jane Doe", "email": "jane@example.com",
      "phone": "+1234567890", "city": "Los Angeles", "status": "Active" }
  ]
}
```

### `GET /api/patients/<pk>/`
Single patient with their appointments.

### `GET /api/appointments/?date=YYYY-MM-DD&status=pending`
Filterable appointment list (up to 100).

### `GET /api/employees/`
All employees.

---

## Production Checklist

Before deploying to production:

- [ ] **`SECRET_KEY`** — generate a new random key, never use the dev default
- [ ] **`DEBUG=False`** in `.env`
- [ ] **Database** — switch from SQLite to PostgreSQL or MySQL
- [ ] **`ALLOWED_HOSTS`** — set to your actual domain in `settings.py`
- [ ] **Static files** — run `python manage.py collectstatic` and serve via nginx/CDN
- [ ] **HTTPS + HSTS** — configure in your web server (nginx/caddy); set `SECURE_SSL_REDIRECT=True` in settings
- [ ] **Email** — configure `EMAIL_BACKEND` to use real SMTP credentials
- [ ] **Media files** — configure persistent storage (local disk or S3-compatible)
- [ ] **Redis cache** — replace `LocMemCache` with Redis for multi-worker deployments
- [ ] **Gunicorn/uWSGI** — don't use `runserver` in production
- [ ] **Logs** — verify `logs/` directory is writable and monitored

Example production settings additions:
```python
SECURE_SSL_REDIRECT       = True
SECURE_HSTS_SECONDS       = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD       = True
SESSION_COOKIE_SECURE     = True
CSRF_COOKIE_SECURE        = True
```

---

## Troubleshooting

**`staticfiles.W004` warning on startup**
```bash
mkdir -p static
```
This is a non-fatal warning — the `static/` directory doesn't exist yet. Creating it removes the warning.

**`ImproperlyConfigured: AUTH_USER_MODEL` error**
Make sure `authentication` is listed before `clinic` in `INSTALLED_APPS` in `settings.py`.

**Images not loading after upload**
Check that `MEDIA_URL` and `MEDIA_ROOT` are set in `settings.py` and that `static(settings.MEDIA_URL, ...)` is appended to `urlpatterns` in `core/urls.py`. Both are already configured in this project.

**PDF generation fails**
`xhtml2pdf` requires `reportlab` and `lxml`. Both are in `requirements.txt`. If the error persists:
```bash
pip install --upgrade xhtml2pdf reportlab lxml
```

**`OperationalError: no such table`**
You haven't run migrations yet:
```bash
python manage.py migrate
```

**Forgot admin password**
```bash
python manage.py changepassword <username>
```

---

*DentCare — April 2026 — v1.0*
