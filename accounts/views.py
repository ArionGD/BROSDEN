from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, KYCForm
from .models import KYC
from .ocr_utils import verify_id_document

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


def _shared_kyc_logic(request, template_name):
    """Shared core logic for KYC processing with OCR."""
    kyc = getattr(request.user, 'kyc', None)
    is_verified = kyc.is_verified if kyc else False

    if request.method == 'POST':
        if is_verified:
            messages.info(request, "Your KYC is already verified. You cannot modify it.")
            return redirect(request.path)
            
        form = KYCForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            kyc_obj = form.save(commit=False)
            kyc_obj.user = request.user

            # Determine which image to OCR based on ID type
            img_to_verify = None
            if kyc_obj.id_type == 'AADHAAR':
                img_to_verify = kyc_obj.aadhaar_image
            elif kyc_obj.id_type == 'PAN':
                img_to_verify = kyc_obj.pan_image

            if img_to_verify:
                kyc_obj.save()  # Save first so that .path is available
                extracted_no = verify_id_document(kyc_obj.id_type, img_to_verify.path)

                if extracted_no:
                    kyc_obj.extracted_id_no = extracted_no
                    user_no = kyc_obj.id_number.replace(" ", "")

                    if user_no == extracted_no:
                        kyc_obj.is_verified = True
                        kyc_obj.verification_score = 100.0
                        messages.success(request, f"✅ OCR Match! {kyc_obj.id_type} verified instantly.")
                    else:
                        messages.warning(request, f"⚠️ OCR extracted '{extracted_no}' but you entered '{kyc_obj.id_number}'. Pending manual review.")
                else:
                    messages.warning(request, "⚠️ OCR could not read your ID clearly. Submitted for manual review.")
            else:
                kyc_obj.is_verified = False

            kyc_obj.save()
            return redirect(request.user.get_dashboard_url())
    else:
        form = KYCForm(instance=kyc)
        if is_verified:
            for field in form.fields.values():
                field.widget.attrs['disabled'] = 'disabled'
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' opacity-70 cursor-not-allowed bg-slate-100'

    base_template = 'tenant/portal_base.html' if request.user.role == 'TENANT' else 'owner/portal_base.html'
    return render(request, template_name, {
        'form': form, 
        'is_verified': is_verified, 
        'kyc': kyc,
        'base_template': base_template
    })


@login_required
def tenant_kyc_view(request):
    if request.user.role != 'TENANT':
        return redirect('index')
    return _shared_kyc_logic(request, 'accounts/tenant_kyc.html')


@login_required
def owner_kyc_view(request):
    if request.user.role != 'OWNER':
        return redirect('index')
    return _shared_kyc_logic(request, 'accounts/owner_kyc.html')

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def profile_view(request):
    from .forms import ProfileUpdateForm
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def account_settings_view(request):
    from .forms import I_CLASS
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        for field in form.fields.values():
            field.widget.attrs['class'] = I_CLASS
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:account_settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        for field in form.fields.values():
            field.widget.attrs['class'] = I_CLASS
    return render(request, 'accounts/account_settings.html', {'form': form})
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('index')
    return redirect('accounts:account_settings')
