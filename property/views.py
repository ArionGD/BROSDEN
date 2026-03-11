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
    """View for Tenants to browse all properties with advanced filtering."""
    properties = Property.objects.all()
    
    # Text Search
    query = request.GET.get('q')
    if query:
        if request.user.is_authenticated:
            SearchActivity.objects.create(user=request.user, query=query)
        properties = properties.filter(models.Q(title__icontains=query) | models.Q(city__icontains=query))

    # --- 1. Universal Base Filters ---
    city = request.GET.get('city')
    if city and city != 'All Cities':
        properties = properties.filter(city__iexact=city)

    p_type = request.GET.get('type')
    if p_type:
        properties = properties.filter(property_type=p_type)

    gender_pref = request.GET.get('gender')
    if gender_pref:
        properties = properties.filter(gender_preference=gender_pref)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)

    available_date = request.GET.get('available_from')
    if available_date:
        properties = properties.filter(available_from__lte=available_date)

    # --- 2. PG & Hostel Specific Filters ---
    sharing = request.GET.get('sharing_type')
    if sharing:
        properties = properties.filter(sharing_type=sharing)

    if request.GET.get('breakfast') == 'on':
        properties = properties.filter(provides_breakfast=True)
    if request.GET.get('full_meals') == 'on':
        properties = properties.filter(provides_breakfast=True, provides_lunch=True, provides_dinner=True)
    
    diet = request.GET.get('diet_type')
    if diet:
        properties = properties.filter(diet_type=diet)

    if request.GET.get('wifi') == 'on':
        properties = properties.filter(wifi_available=True)
    if request.GET.get('laundry') == 'on':
        properties = properties.filter(laundry_service=True)
    if request.GET.get('study_table') == 'on':
        properties = properties.filter(has_study_table=True)
    if request.GET.get('ac') == 'on':
        properties = properties.filter(ac_available=True)

    if request.GET.get('no_curfew') == 'on':
        properties = properties.filter(models.Q(curfew_time__icontains='No') | models.Q(curfew_time='None') | models.Q(curfew_time=''))

    # --- 3. Apartment & Flat Specific Filters ---
    beds = request.GET.get('bedrooms')
    if beds:
        if beds == '4+':
            properties = properties.filter(bedrooms__gte=4)
        else:
            properties = properties.filter(bedrooms=beds)

    furnishing = request.GET.get('furnishing')
    if furnishing:
        properties = properties.filter(furnishing_status=furnishing)

    if request.GET.get('bachelors_allowed') == 'on':
        properties = properties.filter(is_for_students=True)

    parking = request.GET.get('parking')
    if parking:
        properties = properties.filter(parking_type=parking)

    # --- 4. Advanced "Life-Context" Filters ---
    if request.GET.get('verified') == 'on':
        properties = properties.filter(is_verified=True)

    if request.GET.get('pets') == 'on':
        properties = properties.filter(pets_allowed=True)

    properties = properties.order_by('-created_at')
    
    # Metadata for UI
    cities = Property.objects.values_list('city', flat=True).distinct()
    
    wishlist_ids = []
    if request.user.is_authenticated and request.user.role == 'TENANT':
        from wishlist.models import Wishlist
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True)
        
    # Select Template based on context
    if request.user.is_authenticated and request.user.role != 'TENANT':
        template_name = 'property/browse_portal.html'
    else:
        template_name = 'property/browse_public.html'
    
    return render(request, template_name, {
        'properties': properties,
        'wishlist_ids': wishlist_ids,
        'cities': cities,
        'request_params': request.GET
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
        return redirect('accounts:owner_kyc')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
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
        form = PropertyForm(request.POST, request.FILES, instance=prop)
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

