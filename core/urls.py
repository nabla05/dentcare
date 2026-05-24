from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.defaults import page_not_found, server_error, permission_denied

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth app (canonical: /auth/login/ etc.)
    path('auth/', include('authentication.urls')),

    # Short aliases matching CDC spec (/login/, /register/, /logout/)
    path('login/',    RedirectView.as_view(pattern_name='authentication:login',    permanent=False)),
    path('register/', RedirectView.as_view(pattern_name='authentication:register', permanent=False)),
    path('logout/',   RedirectView.as_view(pattern_name='authentication:logout',   permanent=False)),

    # App URLs
    path('', include('clinic.urls')),
    path('', include('billing.urls')),
    path('', include('home.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ─── Custom error handlers ────────────────────────────────────
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
handler403 = 'django.views.defaults.permission_denied'
