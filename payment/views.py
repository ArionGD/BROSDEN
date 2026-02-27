from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import KYCForm
from .models import KYC, PaymentReceipt
from booking.models import BookingRequest
from contract.utils import generate_contract

@login_required
def kyc_form_view(request):
    """View to handle common KYC registration for both roles."""
    if hasattr(request.user, 'kyc') and request.user.kyc.is_verified:
        messages.info(request, "Your KYC is already verified.")
        return redirect('index')

    kyc = getattr(request.user, 'kyc', None)

    if request.method == 'POST':
        form = KYCForm(request.POST, instance=kyc)
        if form.is_valid():
            kyc_obj = form.save(commit=False)
            kyc_obj.user = request.user
            kyc_obj.is_verified = True # Auto-verify for simulation
            kyc_obj.save()
            messages.success(request, "KYC submitted and verified successfully!")
            return redirect(request.GET.get('next', 'index'))
    else:
        form = KYCForm(instance=kyc)
    
    return render(request, 'payment/kyc_form.html', {
        'form': form, 
        'portal_base': request.user.portal_base
    })

@login_required
def razorpay_checkout(request):
    """Interface mimicking Razorpay payment process."""
    amount = request.GET.get('amount', '500')
    item = request.GET.get('item', 'Security Deposit')
    booking_id = request.GET.get('booking_id')
    
    context = {
        'amount': amount,
        'item': item,
        'user': request.user,
        'booking_id': booking_id
    }
    return render(request, 'payment/razorpay_interface.html', context)

@login_required
def payment_success(request, booking_id):
    """Callback view to handle successful payment."""
    booking = get_object_or_404(BookingRequest, id=booking_id, tenant=request.user)
    
    # Mark as PAID
    booking.status = 'PAID'
    booking.save()
    
    # Create Payment Receipt
    receipt = PaymentReceipt.objects.create(
        user=request.user,
        booking=booking,
        property_title=booking.property.title,
        amount=booking.property.price,
        transaction_id=f"TID_{booking.id}_{booking.tenant.id}_{timezone.now().strftime('%U%H%M')}",
        payment_type='SECURITY_DEPOSIT'
    )
    
    # Generate Contract Automatically
    contract = generate_contract(booking)
    
    try:
        from mailer.services import send_contract_created_email
        send_contract_created_email(contract, request.user, request)
        send_contract_created_email(contract, booking.property.owner, request)
    except Exception:
        pass
        
    try:
        from notifications.models import send_notification
        send_notification(request.user, "Payment Successful", f"Your security deposit for {booking.property.title} was received.", 'PAYMENT')
        send_notification(booking.property.owner, "Payment Received", f"Security deposit for {booking.property.title} was paid by {request.user.username}.", 'PAYMENT')
    except Exception:
        pass
        
    context = {
        'booking': booking,
        'contract': contract,
        'receipt': receipt,
        'amount': receipt.amount,
        'transaction_id': receipt.transaction_id
    }
    
    messages.success(request, f"Payment successful! Security Deposit for {booking.property.title} received.")
    return render(request, 'payment/payment_success.html', context)

@login_required
def view_receipt(request, receipt_id):
    """View to display a specific payment receipt."""
    receipt = get_object_or_404(PaymentReceipt, id=receipt_id, user=request.user)
    return render(request, 'payment/receipt_view.html', {'receipt': receipt})
