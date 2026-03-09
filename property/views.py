from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Property
from .forms import PropertyForm
from analytics.models import PropertyView, SearchActivity
from accounts.decorators import tenant_required, owner_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

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
    if not request.user.is_kyc_verified:
        messages.warning(request, "Please complete your KYC verification before listing a property.")
        return redirect('payment:owner_kyc')

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()
            
            # Handle Multiple Images (Limit to 10)
            images = request.FILES.getlist('images')[:10]
            from .models import PropertyImage
            for img in images:
                PropertyImage.objects.create(property=prop, image=img)
                
            messages.success(request, "Property listed successfully!")
            return redirect('property:owner_list')
    else:
        form = PropertyForm()
    return render(request, 'property/add_form.html', {'form': form})

@owner_required
def edit_property(request, pk):
    """View for Owners to edit an existing property."""
    prop = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            
            # Handle New Images (Total limit 10)
            existing_count = prop.images.count()
            allowed_new = max(0, 10 - existing_count)
            images = request.FILES.getlist('images')[:allowed_new]
            
            from .models import PropertyImage
            for img in images:
                PropertyImage.objects.create(property=prop, image=img)
                
            if len(request.FILES.getlist('images')) > allowed_new:
                messages.warning(request, f"Some images were not uploaded because the limit of 10 photos has been reached.")
            
            messages.success(request, "Property updated successfully!")
            return redirect('property:owner_list')
    else:
        form = PropertyForm(instance=prop)
    
    return render(request, 'property/add_form.html', {
        'form': form,
        'is_edit': True,
        'property': prop
    })

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
        
    # Calculate booking options (next 3 months, 1st date)
    from datetime import timedelta
    from django.utils import timezone
    
    current_date = timezone.now().date()
    # Find the 1st of the next month
    if current_date.month == 12:
        next_month_start = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        next_month_start = current_date.replace(month=current_date.month + 1, day=1)
    
    booking_options = []
    temp_date = next_month_start
    for _ in range(3):
        booking_options.append({
            'value': temp_date.strftime('%Y-%m-%d'),
            'label': temp_date.strftime('%B 1st, %Y')
        })
        # Move to 1st of next month
        if temp_date.month == 12:
            temp_date = temp_date.replace(year=temp_date.year + 1, month=1)
        else:
            temp_date = temp_date.replace(month=temp_date.month + 1)

    from feedback.models import MonthlyFeedback
    monthly_feedbacks = MonthlyFeedback.objects.filter(property=prop).order_by('-submitted_at')

    return render(request, 'property/detail.html', {
        'property': prop,
        'is_wishlisted': is_wishlisted,
        'booking_options': booking_options,
        'monthly_feedbacks': monthly_feedbacks
    })

@owner_required
@require_POST
def delete_property_image(request, pk):
    """AJAX view to delete a specific property image."""
    from .models import PropertyImage
    img = get_object_or_404(PropertyImage, pk=pk, property__owner=request.user)
    img.delete()
    return JsonResponse({'status': 'ok'})

