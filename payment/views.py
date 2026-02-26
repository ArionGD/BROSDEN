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
    try:
        kyc = request.user.kyc
        if kyc.is_verified:
            messages.info(request, "Your KYC is already verified.")
            return redirect('index')
    except KYC.DoesNotExist:
        kyc = None

    if request.method == 'POST':
        form = KYCForm(request.POST, instance=kyc)
        if form.is_valid():
            kyc_obj = form.save(commit=False)
            kyc_obj.user = request.user
            # For this demo, we auto-verify to keep it smooth
            kyc_obj.is_verified = True 
            kyc_obj.save()
            messages.success(request, "KYC submitted and verified successfully!")
            
            # Check where they came from
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
    else:
        form = KYCForm(instance=kyc)
    
    # Identify the correct base template based on role
    base_template = 'base.html'
    if request.user.is_authenticated:
        if request.user.role == 'OWNER':
            base_template = 'owner/portal_base.html'
        else:
            base_template = 'tenant/portal_base.html'
            
    return render(request, 'payment/kyc_form.html', {
        'form': form, 
        'base_template': base_template
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
