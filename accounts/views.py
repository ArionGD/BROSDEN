from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            try:
                from mailer.services import send_welcome_email
                send_welcome_email(user, form.cleaned_data['password'], request)
            except Exception as e:
                pass # Fail silently if mailer is not fully configured

            try:
                from notifications.models import send_notification
                send_notification(user, "Welcome!", "Your account has been created successfully.", 'SYSTEM')
            except Exception as e:
                pass
                
            messages.success(request, "Registration successful! You can now login. Check your email for your credentials.")
            return redirect('accounts:login')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect(user.get_dashboard_url())
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')
