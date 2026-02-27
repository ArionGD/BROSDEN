from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Property
from .forms import PropertyForm
from analytics.models import PropertyView, SearchActivity
from accounts.decorators import tenant_required, owner_required

from django.contrib.auth.decorators import login_required

def browse_properties(request):
    """View for Tenants to browse all properties."""
    query = request.GET.get('q')
    properties = Property.objects.all()
    if query:
        # Track search if authenticated
        if request.user.is_authenticated:
            SearchActivity.objects.create(user=request.user, query=query)
            
        properties = properties.filter(title__icontains=query) | properties.filter(city__icontains=query)
    properties = properties.order_by('-created_at')
    
    wishlist_ids = []
    if request.user.is_authenticated and request.user.role == 'TENANT':
        from wishlist.models import Wishlist
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True)
        
    return render(request, 'property/browse.html', {
        'properties': properties,
        'wishlist_ids': wishlist_ids
    })

@owner_required
def owner_property_list(request):
    """View for Owners to see their own listings."""
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'property/owner_list.html', {'properties': properties})

@owner_required
def add_property(request):
    """View for Owners to add a new property."""
    # Enforce KYC
    if not request.user.is_kyc_verified:
        messages.warning(request, "Please complete your KYC verification before listing a property.")
        return redirect('/payment/kyc/?next=' + request.path)

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()
            messages.success(request, "Property listed successfully!")
            return redirect('property:owner_list')
    else:
        form = PropertyForm()
    return render(request, 'property/add_form.html', {'form': form})

@login_required
def property_detail(request, pk):
    """Public/Shared view for property details."""
    prop = get_object_or_404(Property, pk=pk)
    
    # Track view if authenticated
    if request.user.is_authenticated:
        PropertyView.objects.create(property=prop, viewer=request.user)
        
    is_wishlisted = False
    if request.user.is_authenticated and request.user.role == 'TENANT':
        from wishlist.models import Wishlist
        is_wishlisted = Wishlist.objects.filter(user=request.user, property=prop).exists()
        
    return render(request, 'property/detail.html', {
        'property': prop,
        'is_wishlisted': is_wishlisted
    })
