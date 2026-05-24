import time
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse

from .models import MaintenanceMode


# ═══════════════════════════════════════════════════════
#  1. MAINTENANCE MODE
# ═══════════════════════════════════════════════════════

class MaintenanceModeMiddleware:
    """Return HTTP 503 for non-staff users when maintenance mode is on."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/admin/'):
            try:
                mode = MaintenanceMode.objects.get(id=1)
            except MaintenanceMode.DoesNotExist:
                mode = None

            if mode and mode.enabled:
                is_staff = (
                    request.user.is_authenticated and
                    (request.user.is_staff or getattr(request.user, 'role', '') == 'admin')
                )
                if not is_staff:
                    return render(request, 'clinic/maintenance.html', status=503)

        return self.get_response(request)


# ═══════════════════════════════════════════════════════
#  2. PDF Content-Disposition MIDDLEWARE  (CDC §8.2)
# ═══════════════════════════════════════════════════════

class PDFInlineMiddleware:
    """
    Every PDF served through the application gets:
        Content-Disposition: inline; filename="file.pdf"
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        ct = response.get('Content-Type', '')
        if 'application/pdf' in ct:
            if 'Content-Disposition' not in response:
                response['Content-Disposition'] = 'inline; filename="file.pdf"'
        return response


# ═══════════════════════════════════════════════════════
#  3. SECURITY HEADERS  (CDC §7.6)
# ═══════════════════════════════════════════════════════

class SecurityHeadersMiddleware:
    """
    Injects CSP and other security headers on every response.
    """

    CSP = (
        "default-src 'self'; "
        "style-src 'self' fonts.googleapis.com cdnjs.cloudflare.com "
            "cdn.jsdelivr.net 'unsafe-inline'; "
        "script-src 'self' cdnjs.cloudflare.com stackpath.bootstrapcdn.com "
            "cdn.jsdelivr.net 'unsafe-inline' 'unsafe-eval'; "
        "font-src 'self' fonts.gstatic.com cdn.jsdelivr.net; "
        "frame-src 'self' mozilla.github.io; "
        "img-src 'self' data: images.unsplash.com; "
        "frame-ancestors 'self';"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Frame-Options']           = 'SAMEORIGIN'
        response['X-Content-Type-Options']    = 'nosniff'
        response['Referrer-Policy']           = 'strict-origin-when-cross-origin'
        response['Content-Security-Policy']   = self.CSP
        return response


# ═══════════════════════════════════════════════════════
#  4. RATE LIMITER  (CDC §8.6 — login + booking)
# ═══════════════════════════════════════════════════════

RATE_LIMIT_PATHS = {
    '/auth/login/':              (10, 60),   # 10 requests / 60 seconds
    '/login/':                   (10, 60),
    '/book/':                    (5,  60),   # 5 booking attempts / 60 s
    '/patients/appointment/request/': (5, 60),
}


class RateLimitMiddleware:
    """
    Simple IP-based rate limiting using Django's cache (LocMemCache in dev).
    Returns 429 Too Many Requests when the limit is exceeded.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '0.0.0.0')

    def __call__(self, request):
        if request.method == 'POST':
            for path, (limit, window) in RATE_LIMIT_PATHS.items():
                if request.path.startswith(path):
                    ip  = self._get_ip(request)
                    key = f'rl:{path}:{ip}'
                    hits = cache.get(key, 0)
                    if hits >= limit:
                        return HttpResponse(
                            '<h2>429 — Too Many Requests</h2>'
                            '<p>Please slow down and try again in a minute.</p>',
                            status=429,
                            content_type='text/html',
                        )
                    cache.set(key, hits + 1, window)
                    break

        return self.get_response(request)
