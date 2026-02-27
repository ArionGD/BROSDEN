from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

def _handle_post_registration(request, user, password):
    """Helper to send welcome emails and notifications after registration."""
    try:
        from mailer.services import send_welcome_email
        send_welcome_email(user, password, request)
    except Exception:
        pass 

    try:
        from notifications.models import send_notification
        send_notification(user, "Welcome!", "Your account has been created successfully.", 'SYSTEM')
    except Exception:
        pass

def register_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        _handle_post_registration(request, user, form.cleaned_data['password'])
            
        messages.success(request, "Registration successful! Please login with your credentials.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")
        return redirect(user.get_dashboard_url())
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')
