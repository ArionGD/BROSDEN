from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from property.models import Property
from accounts.decorators import tenant_required, owner_required

@tenant_required
def add_review(request, property_id):
    """View for tenants to submit a review."""
    prop = get_object_or_404(Property, id=property_id)
    
    # Check if user already reviewed
    if Review.objects.filter(property=prop, tenant=request.user).exists():
        messages.warning(request, "You have already reviewed this property.")
        return redirect('property:detail', pk=property_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = prop
            review.tenant = request.user
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('property:detail', pk=property_id)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/add_review.html', {
        'form': form,
        'property': prop,
        'portal_base': 'tenant/portal_base.html'
    })

@owner_required
def owner_reviews_list(request):
    """View for owners to see reviews for their properties."""
    reviews = Review.objects.filter(property__owner=request.user).select_related('property', 'tenant')
    
    return render(request, 'reviews/owner_reviews.html', {
        'reviews': reviews,
        'portal_base': 'owner/portal_base.html'
    })

def property_reviews_partial(request, property_id):
    """Partial view to render reviews on a property detail page."""
    reviews = Review.objects.filter(property_id=property_id).select_related('tenant')
    return render(request, 'reviews/_reviews_list.html', {'reviews': reviews})
