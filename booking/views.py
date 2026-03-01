from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from property.models import Property
from .models import BookingRequest
from accounts.decorators import tenant_required, owner_required


@tenant_required
def create_booking(request, property_id):
    """Allow tenants to request a booking."""
    # Enforce KYC before allowing booking
    # Enforce KYC before allowing booking
    if not request.user.is_kyc_verified:
        messages.warning(request, "Please complete your KYC verification before requesting a booking.")
        return redirect(f"{reverse('payment:tenant_kyc')}?next={request.path}")

    prop = get_object_or_404(Property, id=property_id)

    # Prevent duplicate pending requests
    if BookingRequest.objects.filter(property=prop, tenant=request.user, status='PENDING').exists():
        messages.warning(request, "You already have a pending request for this property.")
        return redirect('property:detail', pk=property_id)

    if request.method == 'POST':
        message = request.POST.get('message', '')
        start_date_str = request.POST.get('start_date', '')
        
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Ensure it's the 1st of the month
            if start_date.day != 1:
                start_date = start_date.replace(day=1)
        except (ValueError, TypeError):
            messages.error(request, "Invalid start date selected.")
            return redirect('property:detail', pk=property_id)

        booking = BookingRequest.objects.create(
            property=prop, 
            tenant=request.user, 
            message=message,
            start_date=start_date
        )
        
        try:
            from notifications.models import send_notification
            send_notification(prop.owner, "New Booking Request", f"You have a new booking request for {prop.title} from {request.user.username}.", 'BOOKING')
        except Exception:
            pass

        messages.success(request, "Booking request sent successfully!")
        return redirect('booking:tenant_bookings')

    return redirect('property:detail', pk=property_id)


@tenant_required
def tenant_booking_list(request):
    """View for Tenants to see their own booking requests."""
    bookings = BookingRequest.objects.filter(tenant=request.user)
    return render(request, 'booking/tenant_list.html', {'bookings': bookings})


@owner_required
def owner_booking_list(request):
    """View for Owners to see requests for their properties."""
    bookings = BookingRequest.objects.filter(property__owner=request.user)
    return render(request, 'booking/owner_list.html', {'bookings': bookings})


@owner_required
def handle_booking(request, booking_id, action):
    """Allow Owners to approve or reject requests."""
    booking = get_object_or_404(BookingRequest, id=booking_id, property__owner=request.user)

    if action == 'approve':
        booking.status = 'APPROVED'
        try:
            from mailer.services import send_booking_approved_email
            send_booking_approved_email(booking, request)
        except Exception:
            pass
            
        try:
            from notifications.models import send_notification
            send_notification(booking.tenant, "Booking Approved", f"Your booking for {booking.property.title} has been approved!", 'BOOKING')
        except Exception:
            pass
            
        messages.success(request, f"Booking for {booking.property.title} approved!")
    elif action == 'reject':
        booking.status = 'REJECTED'
        try:
            from notifications.models import send_notification
            send_notification(booking.tenant, "Booking Rejected", f"Your booking for {booking.property.title} was rejected.", 'BOOKING')
        except Exception:
            pass
        messages.warning(request, f"Booking for {booking.property.title} rejected.")

    booking.save()
    return redirect('booking:owner_bookings')
