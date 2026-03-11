import math
from django.shortcuts import render
from django.http import JsonResponse
from property.models import Property
from django.db.models import Avg

def fullscreen_map(request):
    """View for full screen map showing all/selected properties."""
    focus_id = request.GET.get('focus')
    properties = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    # If the user is an owner, show ONLY their properties in the map explorer
    if hasattr(request.user, 'role') and request.user.role == 'OWNER':
        properties = properties.filter(owner=request.user)
    
    # Determine base template based on role
    base_template = 'tenant/portal_base.html' if hasattr(request.user, 'role') and request.user.role == 'TENANT' else 'owner/portal_base.html'
    
    map_title = "My Property Portfolio" if hasattr(request.user, 'role') and request.user.role == 'OWNER' else "Global Explorer"
    
    return render(request, 'map/fullscreen_map.html', {
        'properties': properties,
        'focus_id': focus_id,
        'base_template': base_template,
        'map_title': map_title
    })

def smart_recommend_api(request):
    """API for weighted property recommendation scoring."""
    try:
        dest_lat = float(request.GET.get('lat', 0))
        dest_lng = float(request.GET.get('lng', 0))
        
        # Weights (0-100)
        w_dist = float(request.GET.get('w_dist', 33.3))
        w_price = float(request.GET.get('w_price', 33.3))
        w_rating = float(request.GET.get('w_rating', 33.4))
        
        # Total weight for normalization
        total_w = w_dist + w_price + w_rating
        if total_w == 0: total_w = 1
        
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
                (s_dist * w_dist) + 
                (s_price * w_price) + 
                (s_rating * w_rating)
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
