from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Contract, RentSchedule
from payment.models import PaymentReceipt
from core.notifications import send_simulated_whatsapp


def _check_contract_access(user, contract):
    """Shared access guard: only tenant or property owner may view."""
    return user == contract.booking.tenant or user == contract.booking.property.owner


@login_required
def view_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if not _check_contract_access(request.user, contract):
        return render(request, '403.html', status=403)
    return render(request, 'contract/view_contract.html', {'contract': contract})


@login_required
def view_deposit_receipt(request, receipt_id):
    """Dedicated receipt for the Security Deposit payment."""
    receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
    if not (request.user == receipt.user or request.user == receipt.booking.property.owner):
        return render(request, '403.html', status=403)
        
    return render(request, 'contract/view_deposit.html', {
        'receipt': receipt,
        'portal_base': request.user.portal_base
    })


@login_required
def view_contract_receipt(request, contract_id):
    """Acknowledgment receipt for the Contract execution."""
    contract = get_object_or_404(Contract, id=contract_id)
    if not _check_contract_access(request.user, contract):
        return render(request, '403.html', status=403)
    return render(request, 'contract/receipt_contract.html', {'contract': contract})
@login_required
def sign_contract(request, contract_id):
    """Handles digital signature for contracts."""
    contract = get_object_or_404(Contract, id=contract_id)
    if not _check_contract_access(request.user, contract):
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        if request.user == contract.booking.tenant:
            contract.is_signed_by_tenant = True
        elif request.user == contract.booking.property.owner:
            contract.is_signed_by_owner = True
            
        if contract.is_signed_by_tenant and contract.is_signed_by_owner:
            contract.signed_at = timezone.now()
            # Generate rent schedule upon full execution
            contract.generate_schedule()
            
            # Simulated WhatsApp notification (Timeline Week 3/5)
            send_simulated_whatsapp(request, "Registered Phone", 
                f"Congratulations! Your contract for {contract.booking.property.title} is now fully executed. Rent schedule is generated.")
            
        contract.save()
        messages.success(request, "Contract signed successfully!")
        
        # Redirect back to onboarding or where they came from
        onboarding = getattr(contract.booking, 'onboarding', None)
        if onboarding:
            return redirect('onboarding:dashboard', process_id=onboarding.id)
        return redirect('contract:view_contract', contract_id=contract.id)

    return redirect('contract:view_contract', contract_id=contract.id)

@login_required
def rent_dashboard(request):
    """View for tenants/owners to manage rent payments."""
    if request.user.role == 'TENANT':
        # Get all rent schedules for this tenant's contracts
        schedules = RentSchedule.objects.filter(contract__booking__tenant=request.user)
        template = 'contract/rent_tenant.html'
    else:
        # Get all rent schedules for properties owned by this user
        schedules = RentSchedule.objects.filter(contract__booking__property__owner=request.user)
        template = 'contract/rent_owner.html'
        
    return render(request, template, {
        'schedules': schedules,
        'portal_base': request.user.portal_base
    })
