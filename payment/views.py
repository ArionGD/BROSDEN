from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import KYCForm
from .models import KYC, PaymentReceipt
from booking.models import BookingRequest
from contract.utils import generate_contract

def _shared_kyc_logic(request, template_name):
    """Shared core logic for KYC processing."""
    if hasattr(request.user, 'kyc') and request.user.kyc.is_verified:
        messages.info(request, "Your KYC is already verified.")
        return redirect(request.user.get_dashboard_url())

    kyc = getattr(request.user, 'kyc', None)

    if request.method == 'POST':
        form = KYCForm(request.POST, instance=kyc)
        if form.is_valid():
            kyc_obj = form.save(commit=False)
            kyc_obj.user = request.user
            kyc_obj.is_verified = True 
            kyc_obj.save()
            messages.success(request, "KYC verified successfully!")
            return redirect(request.user.get_dashboard_url())
    else:
        form = KYCForm(instance=kyc)
    
    return render(request, template_name, {'form': form})

@login_required
def tenant_kyc_view(request):
    if request.user.role != 'TENANT':
        return redirect('index')
    return _shared_kyc_logic(request, 'payment/tenant_kyc.html')

@login_required
def owner_kyc_view(request):
    if request.user.role != 'OWNER':
        return redirect('index')
    return _shared_kyc_logic(request, 'payment/owner_kyc.html')

@login_required
def razorpay_checkout(request):
    """Interface mimicking Razorpay payment process with financial breakdown."""
    booking_id = request.GET.get('booking_id')
    payment_type = request.GET.get('type', 'SECURITY_DEPOSIT') # Default to security deposit
    
    if not booking_id:
        return redirect('booking:tenant_bookings')
        
    booking = get_object_or_404(BookingRequest, id=booking_id, tenant=request.user)
    
    if payment_type == 'RENT':
        amount = booking.property.price
        item = f"Monthly Rent for {booking.property.title}"
        breakdown = None # Rent doesn't need the same breakdown as initial deposit
    else:
        breakdown = booking.property.get_financial_breakdown()
        amount = breakdown['total']
        item = f"Security Deposit + Contract Fee for {booking.property.title}"
    
    context = {
        'booking': booking,
        'booking_id': booking.id,
        'breakdown': breakdown,
        'amount': amount,
        'item': item,
        'user': request.user,
        'payment_type': payment_type
    }
    return render(request, 'payment/razorpay_interface.html', context)

@login_required
def payment_success(request, booking_id):
    """Callback view to handle successful payment with financial breakdown."""
    booking = get_object_or_404(BookingRequest, id=booking_id, tenant=request.user)
    payment_type = request.GET.get('type', 'SECURITY_DEPOSIT')
    
    if payment_type == 'RENT':
        # Logic for monthly rent payment
        amount = booking.property.price
        receipt = PaymentReceipt.objects.create(
            user=request.user,
            booking=booking,
            property_title=booking.property.title,
            amount=amount,
            transaction_id=f"RENT_{booking.id}_{booking.tenant.id}_{timezone.now().strftime('%U%H%M')}",
            payment_type='RENT',
            period_month=timezone.now().month,
            period_year=timezone.now().year
        )
        
        try:
            from notifications.models import send_notification
            send_notification(request.user, "Rent Payment Successful", f"Your monthly rent for {booking.property.title} was received.", 'PAYMENT')
            send_notification(booking.property.owner, "Rent Received", f"Monthly rent for {booking.property.title} was paid by {request.user.username}.", 'PAYMENT')
        except Exception:
            pass

        messages.success(request, f"Monthly rent for {booking.property.title} paid successfully!")
        
        context = {
            'booking': booking,
            'receipt': receipt,
            'amount': receipt.amount,
            'transaction_id': receipt.transaction_id,
            'payment_type': 'RENT'
        }
    else:
        # Original Security Deposit Logic
        breakdown = booking.property.get_financial_breakdown()
        booking.status = 'PAID'
        booking.save()
        
        receipt = PaymentReceipt.objects.create(
            user=request.user,
            booking=booking,
            property_title=booking.property.title,
            amount=breakdown['total'],
            security_deposit_amount=breakdown['security_deposit'],
            contract_fee_amount=breakdown['contract_fee'],
            transaction_id=f"TID_{booking.id}_{booking.tenant.id}_{timezone.now().strftime('%U%H%M')}",
            payment_type='SECURITY_DEPOSIT'
        )
        
        contract = generate_contract(booking)
        
        try:
            from mailer.services import send_contract_created_email
            send_contract_created_email(contract, request.user, request)
            send_contract_created_email(contract, booking.property.owner, request)
        except Exception:
            pass
            
        try:
            from notifications.models import send_notification
            send_notification(request.user, "Payment Successful", f"Your security deposit and contract fee for {booking.property.title} was received.", 'PAYMENT')
            send_notification(booking.property.owner, "Payment Received", f"Security deposit and contract fee for {booking.property.title} was paid by {request.user.username}.", 'PAYMENT')
        except Exception:
            pass

        messages.success(request, f"Payment successful! Security Deposit and Contract Fee for {booking.property.title} received.")
        
        context = {
            'booking': booking,
            'contract': contract,
            'receipt': receipt,
            'breakdown': breakdown,
            'amount': receipt.amount,
            'transaction_id': receipt.transaction_id,
            'payment_type': 'SECURITY_DEPOSIT'
        }
    
    return render(request, 'payment/payment_success.html', context)

@login_required
def view_receipt(request, receipt_id):
    """View to display a specific payment receipt."""
    receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
    # Security: Ensure only participant can view
    if receipt.user != request.user and receipt.booking.property.owner != request.user:
        messages.error(request, "Access denied.")
        return redirect('index')
    return render(request, 'contract/view_deposit.html', {
        'receipt': receipt,
        'portal_base': request.user.portal_base
    })

@login_required
def payment_history(request):
    """View to show payment history (Outbound for Tenants, Inbound for Owners)."""
    if request.user.role == 'OWNER':
        # Received payments
        payments = PaymentReceipt.objects.filter(booking__property__owner=request.user).order_by('-created_at')
        is_owner = True
    else:
        # Paid payments
        payments = PaymentReceipt.objects.filter(user=request.user).order_by('-created_at')
        is_owner = False

    return render(request, 'payment/payment_history.html', {
        'payments': payments,
        'is_owner': is_owner,
        'portal_base': request.user.portal_base
    })
