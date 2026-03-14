import math
from django.shortcuts import render
from django.http import JsonResponse
from property.models import Property
from django.db.models import Avg

from django.db import models

def fullscreen_map(request):
    """View for hybrid map explorer featuring card list and spatial view."""
    properties = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    # If the user is an owner, show ONLY their properties in the map explorer
    if hasattr(request.user, 'role') and request.user.role == 'OWNER':
        properties = properties.filter(owner=request.user)

    # --- APPLY ADVANCED FILTERS (Sync with Browse Page) ---
    query = request.GET.get('q')
    if query:
        properties = properties.filter(models.Q(title__icontains=query) | models.Q(city__icontains=query))

    city = request.GET.get('city')
    if city and city != 'All Cities':
        properties = properties.filter(city__iexact=city)

    p_type = request.GET.get('type')
    if p_type:
        # Map 'FLAT' from UI to 'APARTMENT' in Model
        if p_type == 'FLAT':
            properties = properties.filter(property_type='APARTMENT')
        else:
            properties = properties.filter(property_type=p_type)

    gender_pref = request.GET.get('gender')
    if gender_pref and gender_pref != 'ALL':
        properties = properties.filter(gender_preference=gender_pref)

    max_price = request.GET.get('max_price')
    if max_price:
        try:
            properties = properties.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Specifics: BHK and Sharing
    bhk = request.GET.get('bedrooms')
    if bhk:
        try:
            # Map '0.5' (1 RK) to 0 bedrooms in IntegerField, others to int
            val = float(bhk)
            if val == 0.5:
                properties = properties.filter(bedrooms=0)
            else:
                properties = properties.filter(bedrooms=int(val))
        except ValueError:
            pass

    sharing = request.GET.get('sharing_type')
    if sharing:
        # Map UI numeric values to Model string choices
        sharing_map = {'1': 'SINGLE', '2': 'DOUBLE', '3': 'TRIPLE'}
        sharing_val = sharing_map.get(sharing, sharing)
        properties = properties.filter(sharing_type=sharing_val)

    # Specifics: AC, Meals, WiFi, Laundry
    if request.GET.get('ac') in ['on', 'true']:
        properties = properties.filter(ac_available=True)
    if request.GET.get('meals') in ['on', 'true']:
        properties = properties.filter(food_provided=True)
    if request.GET.get('wifi') in ['on', 'true']:
        properties = properties.filter(wifi_available=True)
    if request.GET.get('laundry') in ['on', 'true']:
        properties = properties.filter(laundry_service=True)

    if request.GET.get('verified') in ['on', 'true']:
        properties = properties.filter(is_verified=True)
    if request.GET.get('pets') in ['on', 'true']:
        properties = properties.filter(pets_allowed=True)

    properties = properties.order_by('-created_at')

    # Metadata
    cities = Property.objects.values_list('city', flat=True).distinct()
    focus_id = request.GET.get('focus')
    
    # Select Template based on context - use portal layout for authenticated members
    if request.user.is_authenticated and request.user.role in ['OWNER', 'ADMIN', 'TENANT']:
        template_name = 'map/portal_map.html'
        map_title = "Property Governance" if request.user.role == 'ADMIN' else "Property Explorer"
    else:
        template_name = 'map/public_map.html'
        map_title = "Property Explorer"
    
    return render(request, template_name, {
        'properties': properties,
        'focus_id': focus_id,
        'map_title': map_title,
        'cities': cities,
        'request_params': request.GET
    })

def smart_recommend_api(request):
    """API for weighted property recommendation scoring."""
    try:
        dest_lat = float(request.GET.get('lat', 0))
        dest_lng = float(request.GET.get('lng', 0))
        
        # Weights (0-100)
        w_dist = float(request.GET.get('w_dist') or 33.3)
        w_price = float(request.GET.get('w_price') or 33.3)
        w_rating = float(request.GET.get('w_rating') or 33.4)
        
        # Total weight for normalization
        total_w = w_dist + w_price + w_rating
        if total_w == 0: total_w = 100 # Fallback to 100 if weights are zero
        
        properties = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        results = []
        
        if not properties.exists():
            return JsonResponse({'results': []})
            
        # Get min/max for normalization
        prices = properties.values_list('price', flat=True)
        min_p, max_p = min(prices), max(prices)
        price_range = max_p - min_p if max_p != min_p else 1
        
        # Pre-calculate distances to find min/max
        prop_data = []
        for p in properties:
            # Simple Euclidean distance for performance (good enough for city scale)
            dist = math.sqrt((p.latitude - dest_lat)**2 + (p.longitude - dest_lng)**2)
            prop_data.append((p, dist))
            
        dists = [d for p, d in prop_data]
        min_d, max_d = min(dists), max(dists)
        dist_range = max_d - min_d if max_d != min_d else 1
        
        for p, dist in prop_data:
            # 1. Distance Score (0 to 1, higher is better/closer)
            # Inverse: (dist - min) / range gives [0, 1] where 1 is furthest.
            # So 1 - (...) gives 1 for closest, 0 for furthest.
            s_dist = 1 - ((dist - min_d) / dist_range)
            
            # 2. Price Score (0 to 1, higher is better/cheaper)
            s_price = 1 - ((p.price - min_p) / price_range)
            
            # 3. Rating Score (0 to 1, higher is better)
            # Using owner's badges/reputation if available, fallback to 0.5
            from accounts.badge_utils import get_owner_badge
            badge = get_owner_badge(p.owner)
            s_rating = (badge['avg'] / 5.0) if badge['avg'] > 0 else 0.5
            
            # Weighted Final Score
            final_score = (
                (float(s_dist) * w_dist) + 
                (float(s_price) * w_price) + 
                (float(s_rating) * w_rating)
            ) / total_w
            
            results.append({
                'id': p.id,
                'score': round(final_score * 100, 1),
                'dist_km': round(dist * 111, 2), # rough approx: 1 deg ~ 111km
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
