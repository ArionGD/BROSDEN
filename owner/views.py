from django.shortcuts import render
from accounts.decorators import owner_required
from payment.models import PaymentReceipt

@owner_required
def dashboard(request):
    return render(request, 'owner/dashboard.html')

@owner_required
def rent_received(request):
    # Fetch all rent receipts for properties owned by this user
    rent_payments = PaymentReceipt.objects.filter(
        booking__property__owner=request.user,
        payment_type='RENT'
    ).order_by('-created_at')
    
    context = {
        'rent_payments': rent_payments,
    }
    return render(request, 'owner/rent_received.html', context)
