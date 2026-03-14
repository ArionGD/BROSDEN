
import os
import django
import math
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from property.models import Property
from django.db.models import Avg

def test_smart_recommend():
    try:
        dest_lat = 23.0371
        dest_lng = 72.5445
        w_dist = 10.0
        w_price = 80.0
        w_rating = 10.0
        
        total_w = w_dist + w_price + w_rating
        if total_w == 0: total_w = 100
        
        properties = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        results = []
        
        if not properties.exists():
            print("No properties found")
            return
            
        prices = properties.values_list('price', flat=True)
        min_p, max_p = min(prices), max(prices)
        price_range = float(max_p - min_p) if max_p != min_p else 1.0
        
        prop_data = []
        for p in properties:
            dist = math.sqrt((float(p.latitude) - dest_lat)**2 + (float(p.longitude) - dest_lng)**2)
            prop_data.append((p, dist))
            
        dists = [d for p, d in prop_data]
        min_d, max_d = min(dists), max(dists)
        dist_range = max_d - min_d if max_d != min_d else 1.0
        
        for p, dist in prop_data:
            s_dist = 1 - ((dist - min_d) / dist_range)
            s_price = 1 - ((float(p.price) - float(min_p)) / price_range)
            
            from accounts.badge_utils import get_owner_badge
            badge = get_owner_badge(p.owner)
            s_rating = (badge['avg'] / 5.0) if badge['avg'] > 0 else 0.5
            
            final_score = (
                (s_dist * w_dist) + 
                (s_price * w_price) + 
                (s_rating * w_rating)
            ) / total_w
            
            results.append({
                'id': p.id,
                'score': round(final_score * 100, 1),
            })
        
        print(f"Success! Found {len(results)} results.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_recommend()
