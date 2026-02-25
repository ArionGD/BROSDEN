from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from property.models import Property
from .models import BookingRequest
from accounts.decorators import tenant_required, owner_required

@tenant_required
def create_booking(request, property_id):
    """Allow tenants to request a booking."""
    prop = get_object_or_404(Property, id=property_id)
    
    # Check if a pending request already exists
    existing = BookingRequest.objects.filter(property=prop, tenant=request.user, status='PENDING').exists()
    if existing:
        messages.warning(request, "You already have a pending request for this property.")
        return redirect('property:detail', pk=property_id)

    if request.method == 'POST':
        message = request.POST.get('message', '')
        BookingRequest.objects.create(
            property=prop,
            tenant=request.user,
            message=message
        )
        messages.success(request, "Booking request sent successfully!")
        return redirect('booking:tenant_bookings')
    
    return redirect('property:detail', pk=property_id)

@tenant_required
def tenant_booking_list(request):
    """View for Tenants to see their own requests."""
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
        messages.success(request, f"Booking for {booking.property.title} approved!")
    elif action == 'reject':
        booking.status = 'REJECTED'
        messages.warning(request, f"Booking for {booking.property.title} rejected.")
    
    booking.save()
    return redirect('booking:owner_bookings')
