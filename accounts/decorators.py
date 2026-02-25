from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login') # We will need to create login later
            
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('index')
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return role_required(allowed_roles=['ADMIN'])(view_func)

def tenant_required(view_func):
    return role_required(allowed_roles=['TENANT'])(view_func)

def owner_required(view_func):
    return role_required(allowed_roles=['OWNER'])(view_func)
