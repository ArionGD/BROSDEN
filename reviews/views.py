from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PropertyReview, TenantReview
from .forms import PropertyReviewForm, TenantReviewForm
from property.models import Property
from booking.models import BookingRequest
from accounts.decorators import tenant_required, owner_required

@tenant_required
def add_property_review(request, booking_id):
    """View for tenants to submit a review for a property they booked."""
    booking = get_object_or_404(BookingRequest, id=booking_id, tenant=request.user)
    
    # Check Requirements
    if not request.user.is_kyc_verified:
        messages.error(request, "You must complete KYC verification before leaving a review.")
        return redirect('accounts:tenant_kyc')
        
    if booking.status != 'PAID':
        messages.error(request, "You can only review a property after a successful booking/payment.")
        return redirect('booking:tenant_bookings')

    if hasattr(booking, 'property_review'):
        messages.warning(request, "You have already reviewed this stay.")
        return redirect('booking:tenant_bookings')

    if request.method == 'POST':
        form = PropertyReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.property = booking.property
            review.tenant = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('booking:tenant_bookings')
    else:
        form = PropertyReviewForm()
    
    return render(request, 'reviews/add_property_review.html', {
        'form': form,
        'booking': booking,
        'portal_base': 'tenant/portal_base.html'
    })

@owner_required
def add_tenant_review(request, booking_id):
    """View for owners to submit a review for a tenant who stayed in their property."""
    booking = get_object_or_404(BookingRequest, id=booking_id, property__owner=request.user)
    
    # Check Requirements
    if not request.user.is_kyc_verified:
        messages.error(request, "You must complete KYC verification before leaving a review.")
        return redirect('accounts:owner_kyc')

    if booking.status != 'PAID':
        messages.error(request, "You can only review a tenant after a completed booking.")
        return redirect('booking:owner_bookings')

    if hasattr(booking, 'tenant_review'):
        messages.warning(request, "You have already reviewed this tenant for this stay.")
        return redirect('booking:owner_bookings')

    if request.method == 'POST':
        form = TenantReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.owner = request.user
            review.tenant = booking.tenant
            review.save()
            messages.success(request, "Tenant review submitted successfully.")
            return redirect('booking:owner_bookings')
    else:
        form = TenantReviewForm()
    
    return render(request, 'reviews/add_tenant_review.html', {
        'form': form,
        'booking': booking,
        'portal_base': 'owner/portal_base.html'
    })

@owner_required
def owner_reviews_list(request):
    """View for owners to see reviews written about their properties."""
    reviews = PropertyReview.objects.filter(property__owner=request.user).select_related('property', 'tenant')
    return render(request, 'reviews/owner_reviews.html', {
        'reviews': reviews,
        'portal_base': 'owner/portal_base.html'
    })

def property_reviews_partial(request, property_id):
    """Partial view to render reviews on a property detail page."""
    reviews = PropertyReview.objects.filter(property_id=property_id).select_related('tenant')
    return render(request, 'reviews/_reviews_list.html', {'reviews': reviews})
