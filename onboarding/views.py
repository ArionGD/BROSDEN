from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import OnboardingProcess, ConditionReport, RoomInventory, UtilityOrService, OrientationGuide
from core.notifications import send_simulated_whatsapp

@login_required
def onboarding_dashboard(request, process_id):
    """View the main onboarding progress for a specific contract."""
    process = get_object_or_404(OnboardingProcess, id=process_id)
    
    # Security Check
    if request.user != process.booking.tenant and request.user != process.booking.property.owner:
        return render(request, '403.html', status=403)
        
    return render(request, 'onboarding/dashboard.html', {
        'process': process,
        'is_owner': request.user == process.booking.property.owner,
        'portal_base': request.user.portal_base
    })

@login_required
def upload_condition_report(request, process_id):
    """Owner uploads visual evidence of room condition."""
    process = get_object_or_404(OnboardingProcess, id=process_id)
    if request.user != process.booking.property.owner:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        if item_name and description:
            ConditionReport.objects.create(
                onboarding=process,
                item_name=item_name,
                description=description,
                image=image,
                owner_verified=True
            )
            messages.success(request, "Condition report item added.")
            return redirect('onboarding:dashboard', process_id=process.id)
            
    return render(request, 'onboarding/upload_condition.html', {'process': process})

@login_required
def confirm_inventory(request, item_id):
    """Tenant confirms item in Room Inventory."""
    item = get_object_or_404(RoomInventory, id=item_id)
    if request.user != item.onboarding.booking.tenant:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        item.is_confirmed_by_tenant = True
        item.save()
        
        # Check if all inventory items are confirmed
        process = item.onboarding
        if not process.inventory_items.filter(is_confirmed_by_tenant=False).exists():
            process.inventory_confirmed = True
            process.save()
            messages.success(request, "All inventory items confirmed!")
        else:
            messages.success(request, f"{item.item_name} marked as received/confirmed.")
            
    return redirect('onboarding:dashboard', process_id=item.onboarding.id)

@login_required
def mark_handover_complete(request, process_id):
    """Owner marks keys handed over and move-in finalized."""
    process = get_object_or_404(OnboardingProcess, id=process_id)
    if request.user != process.booking.property.owner:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        process.keys_handed_over = True
        process.status = 'COMPLETED'
        process.save()
        
        # Simulated WhatsApp notification (Timeline Week 6)
        send_simulated_whatsapp(request, "Registered Phone", 
            f"Keys have been handed over for {process.booking.property.title}! Welcome to your new home.")
        messages.success(request, "Move-in finalized! Property has been handed over.")
        
    return redirect('onboarding:dashboard', process_id=process.id)
