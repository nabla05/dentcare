from .models import ActivityLog
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def log_action(user, action, details=''):
    """Call this anywhere to log an action."""
    ActivityLog.objects.create(
        user=user,
        action=action,
        details=details
    )

def staff_required(view_func):
    """Allow only admin, doctor, and receptionist."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:login')
        if request.user.role not in ('admin', 'doctor', 'receptionist'):
            messages.error(request, "You don't have permission to access this area.")
            return redirect('home:home')
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
def admin_required(view_func):
    """Allow only admin."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:login')
        if request.user.role != 'admin':
            messages.error(request, "Admin access required.")
            return redirect('clinic:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
 