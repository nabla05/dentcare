import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dentcare-dev-fallback-key-change-in-production')
DEBUG      = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# ─── Applications ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'authentication',
    'clinic',
    'billing',
    'home',
]

# ─── Middleware ────────────────────────────────────────────────
# Order matters: RateLimit → Security → Auth → Maintenance → PDF headers
MIDDLEWARE = [
    'clinic.middleware.RateLimitMiddleware',          # must be early to block before auth
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'clinic.middleware.MaintenanceModeMiddleware',
    'clinic.middleware.PDFInlineMiddleware',
    'clinic.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'core.urls'

# ─── Templates ────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ─── Database (SQLite) ───────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   BASE_DIR / 'db.sqlite3',
    }
}

# ─── Cache (LocMemCache for dev — swap to Redis in prod) ──────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dentcare-cache',
    }
}

# ─── Password Validation ──────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Custom User Model ────────────────────────────────────────
AUTH_USER_MODEL = 'authentication.User'

# ─── Internationalization ─────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─── Static & Media ───────────────────────────────────────────
STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Media sub-dirs (created automatically by Django on first upload)
# media/avatars/         — patient avatars
# media/rapports/        — PDF medical reports
# media/diagnosis_photos/ — diagnosis images

# ─── Auth Redirects ───────────────────────────────────────────
LOGIN_URL           = '/auth/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Email ────────────────────────────────────────────────────
# Development: print emails to console
# Production: switch to smtp and fill EMAIL_HOST_* vars
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST          = os.getenv('EMAIL_HOST',     'smtp.gmail.com')
EMAIL_PORT          = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER',     '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.getenv('DEFAULT_FROM_EMAIL',  'noreply@dentcare.com')

# ─── Upload validation ────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
ALLOWED_PDF_EXTENSIONS   = ['.pdf']
MAX_UPLOAD_SIZE_MB       = 10          # 10 MB hard limit
MAX_UPLOAD_SIZE_BYTES    = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# ─── Logging ──────────────────────────────────────────────────
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style':  '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style':  '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    LOGS_DIR / 'dentcare.log',
            'maxBytes':    5 * 1024 * 1024,   # 5 MB
            'backupCount': 5,
            'formatter':   'verbose',
        },
        'file_errors': {
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    LOGS_DIR / 'errors.log',
            'maxBytes':    5 * 1024 * 1024,
            'backupCount': 5,
            'formatter':   'verbose',
            'level':       'ERROR',
        },
    },
    'root': {
        'handlers': ['console', 'file_general'],
        'level':    'INFO',
    },
    'loggers': {
        'django': {
            'handlers':  ['console', 'file_general'],
            'level':     'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers':  ['file_errors', 'console'],
            'level':     'ERROR',
            'propagate': False,
        },
        'clinic': {
            'handlers':  ['console', 'file_general'],
            'level':     'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
