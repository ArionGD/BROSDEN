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
    """View for tenants/owners to manage rent payments with timeline and history."""
    from django.db.models import Q
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    today = date.today()
    prev_date = today - relativedelta(months=1)
    next_date = today + relativedelta(months=1)
    
    if request.user.role == 'TENANT':
        # Get all contracts first to ensure we see them even if schedules aren't generated
        active_contracts = Contract.objects.filter(booking__tenant=request.user)
        # Get all rent schedules for this tenant's contracts
        schedules = RentSchedule.objects.filter(contract__in=active_contracts).order_by('due_date')
        transactions = PaymentReceipt.objects.filter(user=request.user).order_by('-created_at')[:5]
        template = 'contract/rent_tenant.html'
    else:
        active_contracts = Contract.objects.filter(booking__property__owner=request.user)
        schedules = RentSchedule.objects.filter(contract__in=active_contracts).order_by('due_date')
        transactions = PaymentReceipt.objects.filter(booking__property__owner=request.user).order_by('-created_at')[:5]
        template = 'contract/rent_owner.html'
    
    is_owner = (request.user.role == 'OWNER')
        
    # Calculate specific timeline: Prev, Current, Next
    # Filter by both month AND year for accuracy
    timeline = {
        'prev': schedules.filter(due_date__month=prev_date.month, due_date__year=prev_date.year).first(),
        'current': schedules.filter(due_date__month=today.month, due_date__year=today.year).first(),
        'next': schedules.filter(due_date__month=next_date.month, due_date__year=next_date.year).first()
    }

    # Fallback: If current month doesn't have a schedule yet (e.g. contract not fully signed),
    # but a contract exists, create a "virtual" entry for the UI to display.
    if not timeline['current'] and active_contracts.exists():
        first_contract = active_contracts.filter(is_signed_by_tenant=False).first() or active_contracts.first()
        timeline['current'] = {
            'amount': first_contract.booking.property.price,
            'due_date': today, # Approximate
            'status': 'PENDING_SIGNATURE',
            'is_virtual': True,
            'contract_id': first_contract.id
        }

    return render(request, template, {
        'schedules': schedules,
        'transactions': transactions,
        'timeline': timeline,
        'active_contracts': active_contracts,
        'next_cycle_start': (today + relativedelta(months=1)).replace(day=1),
        'portal_base': request.user.portal_base,
        'total_collected': schedules.filter(status='PAID').count() * schedules.first().amount if is_owner and schedules.filter(status='PAID').exists() else 0, # Rough calc
        'current_month_expected': timeline['current'].amount if is_owner and timeline['current'] and not isinstance(timeline['current'], dict) else 0
    })

from accounts.decorators import owner_required

@owner_required
def mark_rent_paid(request, schedule_id):
    """Allow owners to manually acknowledge rent payment."""
    schedule = get_object_or_404(RentSchedule, id=schedule_id, contract__booking__property__owner=request.user)
    
    if request.method == 'POST':
        schedule.status = 'PAID'
        schedule.paid_at = timezone.now()
        schedule.transaction_id = f"MANUAL_{schedule.id}_{timezone.now().strftime('%y%m%d')}"
        schedule.save()
        
        # Notify Tenant
        try:
            from notifications.models import send_notification
            send_notification(schedule.contract.booking.tenant, "Rent Acknowledged", f"Owner has acknowledged your rent payment for {schedule.due_date|date:'F Y'}.", 'PAYMENT')
        except:
            pass
            
        messages.success(request, f"Rent for {schedule.due_date|date:'F'} marked as paid.")
    
    return redirect('contract:rent_dashboard')
