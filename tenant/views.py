from django.shortcuts import render
from accounts.decorators import tenant_required
from booking.models import BookingRequest
from payment.models import PaymentReceipt
from django.utils import timezone
from datetime import timedelta

@tenant_required
def dashboard(request):
    from onboarding.models import OnboardingProcess
    from feedback.models import FeedbackRequest
    onboarding_processes = OnboardingProcess.objects.filter(booking__tenant=request.user).order_by('-created_at')
    pending_feedbacks = FeedbackRequest.objects.filter(contract__booking__tenant=request.user, status='PENDING')
    return render(request, 'tenant/dashboard.html', {
        'onboarding_processes': onboarding_processes,
        'pending_feedbacks': pending_feedbacks
    })


@tenant_required
def rent_payments(request):
    # Find active bookings for the tenant
    active_bookings = BookingRequest.objects.filter(tenant=request.user, status='PAID')
    
    # For now, we take the most recent paid booking as the "active" one
    active_booking = active_bookings.first()
    
    rent_history = []
    next_payment = None
    timeline = []

    if active_booking:
        # Fetch actual payment history
        rent_history = PaymentReceipt.objects.filter(
            user=request.user, 
            booking=active_booking,
            payment_type='RENT'
        ).order_by('-created_at')

        # Logic for timeline: 
        # 1. Start from the month of the first RENT payment, 
        #    OR the current month if no rent has been paid yet.
        current_date = timezone.now()
        
        # Get earliest point for timeline
        if active_booking.start_date:
            timeline_start = active_booking.start_date.replace(day=1)
        else:
            # Fallback for old bookings
            earliest_payment = rent_history.last()
            if earliest_payment and earliest_payment.period_month and earliest_payment.period_year:
                timeline_start = timezone.datetime(
                    year=earliest_payment.period_year, 
                    month=earliest_payment.period_month, 
                    day=1
                ).replace(tzinfo=timezone.get_current_timezone())
            else:
                timeline_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # End at current month + 1
        timeline_end = (current_date + timedelta(days=32)).replace(day=1) 
        
        temp_date = timeline_start
        while temp_date <= timeline_end:
            # Check if this month is paid
            is_paid = PaymentReceipt.objects.filter(
                booking=active_booking,
                payment_type='RENT',
                period_month=temp_date.month,
                period_year=temp_date.year
            ).exists()
            
            status = 'PAID' if is_paid else ('DUE' if temp_date.month == current_date.month and temp_date.year == current_date.year else 'UPCOMING')
            
            # If it's the current month and not paid, check if it's actually "DUE" or "UPCOMING"
            if status == 'DUE' and not is_paid:
                # Basic rule: Rent is due on the 1st
                pass 
            elif temp_date > current_date:
                status = 'UPCOMING'

            timeline.append({
                'month': temp_date.strftime('%B'),
                'year': temp_date.year,
                'status': status,
                'date': temp_date
            })
            
            # Move to next month
            if temp_date.month == 12:
                temp_date = temp_date.replace(year=temp_date.year + 1, month=1)
            else:
                temp_date = temp_date.replace(month=temp_date.month + 1)

        # Calculate next payment details
        monthly_rent = active_booking.property.price
        # Find first unpaid month in timeline
        next_unpaid = next((item for item in timeline if item['status'] != 'PAID'), None)
        
        if next_unpaid:
            next_payment = {
                'amount': monthly_rent,
                'due_date': next_unpaid['date'],
                'is_due': next_unpaid['status'] == 'DUE' or next_unpaid['status'] == 'OVERDUE'
            }
        else:
            next_payment = None

    context = {
        'active_booking': active_booking,
        'rent_history': rent_history,
        'next_payment': next_payment,
        'timeline': timeline,
    }
    return render(request, 'tenant/rent_payments.html', context)
