from django.shortcuts import render, get_object_or_404, redirect
from accounts.decorators import admin_required
from property.models import Property
from booking.models import BookingRequest
from accounts.models import User, KYC
from django.contrib import messages

@admin_required
def dashboard(request):
    """System Admin Overview Dashboard."""
    # Summary Stats
    total_tenants = User.objects.filter(role='TENANT').count()
    total_owners = User.objects.filter(role='OWNER').count()
    total_properties = Property.objects.count()
    total_bookings = BookingRequest.objects.count()
    
    # Recent Activities (Placeholder for now)
    recent_properties = Property.objects.order_by('-created_at')[:5]
    
    context = {
        'total_tenants': total_tenants,
        'total_owners': total_owners,
        'total_properties': total_properties,
        'total_bookings': total_bookings,
        'recent_properties': recent_properties,
    }
    return render(request, 'sys_admin/dashboard.html', context)
    
@admin_required
def user_matrix(request):
    """Deep dive into user demographics and verification status."""
    # Tenant Stats
    tenants = User.objects.filter(role='TENANT')
    tenant_stats = {
        'total': tenants.count(),
        'active': tenants.filter(is_active=True).count(),
        'verified': tenants.filter(kyc__is_verified=True).count(),
        'pending_kyc': tenants.filter(kyc__is_verified=False).count(),
    }
    
    # Owner Stats
    owners = User.objects.filter(role='OWNER')
    owner_stats = {
        'total': owners.count(),
        'active': owners.filter(is_active=True).count(),
        'verified': owners.filter(kyc__is_verified=True).count(),
        'pending_kyc': owners.filter(kyc__is_verified=False).count(),
    }
    
    return render(request, 'sys_admin/user_matrix.html', {
        'tenant_stats': tenant_stats,
        'owner_stats': owner_stats,
    })

@admin_required
def listing_requests(request):
    """View to manage property verification requests."""
    properties = Property.objects.filter(is_verified=False).order_by('-created_at')
    return render(request, 'sys_admin/operations/listing_requests.html', {'properties': properties})

@admin_required
def tenant_kyc(request):
    """View to manage tenant KYC verification."""
    kyc_list = KYC.objects.filter(user__role='TENANT', is_verified=False).order_by('-submitted_at')
    return render(request, 'sys_admin/operations/tenant_kyc.html', {'kyc_list': kyc_list})

@admin_required
def owner_kyc(request):
    """View to manage owner KYC verification."""
    kyc_list = KYC.objects.filter(user__role='OWNER', is_verified=False).order_by('-submitted_at')
    return render(request, 'sys_admin/operations/owner_kyc.html', {'kyc_list': kyc_list})

@admin_required
def tenant_kyc_detail(request, pk):
    """Detailed audit view for a specific tenant's KYC."""
    kyc = get_object_or_404(KYC, pk=pk, user__role='TENANT')
    return render(request, 'sys_admin/operations/tenant_kyc_detail.html', {'kyc': kyc})

@admin_required
def owner_kyc_detail(request, pk):
    """Detailed audit view for a specific owner's KYC."""
    kyc = get_object_or_404(KYC, pk=pk, user__role='OWNER')
    return render(request, 'sys_admin/operations/owner_kyc_detail.html', {'kyc': kyc})

@admin_required
def approve_kyc(request, pk):
    """Manually approve a KYC request."""
    kyc = get_object_or_404(KYC, pk=pk)
    kyc.is_verified = True
    kyc.verification_score = 100.0  # Force 100% on manual approval
    kyc.save()
    
    # Notify User (Internal notification logic)
    try:
        from notifications.models import send_notification
        send_notification(kyc.user, "KYC Verified!", "Your identity has been manually verified by the portal sentinel.", 'SYSTEM')
    except:
        pass
        
    messages.success(request, f"Identity for {kyc.user.username} has been verified.")
    return redirect('sys_admin:tenant_kyc' if kyc.user.role == 'TENANT' else 'sys_admin:owner_kyc')

@admin_required
def reject_kyc(request, pk):
    """Reject a KYC request."""
    kyc = get_object_or_404(KYC, pk=pk)
    kyc.is_verified = False
    kyc.verification_score = 0.0
    kyc.save()
    
    # Notify User
    try:
        from notifications.models import send_notification
        send_notification(kyc.user, "KYC Rejected", "Your identity verification failed. Please re-upload clear documents.", 'SYSTEM')
    except:
        pass

    messages.warning(request, f"Identity for {kyc.user.username} has been rejected.")
    return redirect('sys_admin:tenant_kyc' if kyc.user.role == 'TENANT' else 'sys_admin:owner_kyc')
