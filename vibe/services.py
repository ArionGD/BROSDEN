import requests
from django.utils import timezone
from .models import PropertyVibe

def calculate_property_vibe(property_obj, force=False):
    """
    Calculates the vibe scores for a property using Overpass API (OpenStreetMap).
    Requires the property to have latitude and longitude.
    If force is False and a recent vibe exists (less than 7 days old), returns the existing one.
    """
    if not property_obj.latitude or not property_obj.longitude:
        return None
        
    # Check if a recent vibe exists to avoid spamming the API
    try:
        vibe = property_obj.vibe
        if not force:
            days_old = (timezone.now() - vibe.last_updated).days
            if days_old < 7:
                return vibe
    except PropertyVibe.DoesNotExist:
        vibe = PropertyVibe(property=property_obj)

    lat, lon = property_obj.latitude, property_obj.longitude
    radius = 1500 # 1.5km search radius

    # Define queries for Overpass API
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Categories mapped to OSM tags (using nwr for Node, Way, Relation)
    queries = {
        # Expanded party to include cafes and restaurants since Gujarat is a dry state (pubs are rare), 
        # and SBR is known for cafes.
        'party': f'nwr["amenity"~"pub|bar|nightclub|cafe|restaurant|fast_food"](around:{radius},{lat},{lon});',
        'study': f'nwr["amenity"~"university|college|library|school"](around:{radius},{lat},{lon});',
        'shopping': f'nwr["shop"~"mall|supermarket|department_store|clothes"](around:{radius},{lat},{lon}); nwr["building"~"retail|commercial"](around:{radius},{lat},{lon});',
        'residential': f'nwr["leisure"~"park|playground"](around:{radius},{lat},{lon}); nwr["amenity"~"hospital|clinic"](around:{radius},{lat},{lon}); nwr["landuse"~"residential"](around:{radius},{lat},{lon});',
    }

    scores = {}
    
    try:
        for category, query in queries.items():
            full_query = f"[out:json];({query});out count;"
            response = requests.post(overpass_url, data={'data': full_query}, timeout=10)
            data = response.json()
            
            # Extract count (Sum of nodes, ways, and relations)
            count = 0
            if 'elements' in data and len(data['elements']) > 0:
                tags = data['elements'][0].get('tags', {})
                count += int(tags.get('nodes', 0))
                count += int(tags.get('ways', 0))
                count += int(tags.get('relations', 0))
            scores[category] = count
            
    except Exception as e:
        print(f"Overpass API Error: {e}")
        if vibe.pk:
            return vibe
        return None

    # Normalization (Max expected values per category in 1.5km to reach 100 score)
    MAX_EXPECTED = {
        'party': 40,       # Lots of cafes/restaurants in areas like SBR
        'study': 15,
        'shopping': 30,
        'residential': 40
    }

    # Calculate 0-100 scores
    party_score = min((scores.get('party', 0) / MAX_EXPECTED['party']) * 100, 100)
    study_score = min((scores.get('study', 0) / MAX_EXPECTED['study']) * 100, 100)
    shopping_score = min((scores.get('shopping', 0) / MAX_EXPECTED['shopping']) * 100, 100)
    residential_score = min((scores.get('residential', 0) / MAX_EXPECTED['residential']) * 100, 100)

    # Base minimums if some exist
    if scores.get('party', 0) > 0 and party_score < 10: party_score = 15
    if scores.get('study', 0) > 0 and study_score < 10: study_score = 15
    if scores.get('shopping', 0) > 0 and shopping_score < 10: shopping_score = 15
    if scores.get('residential', 0) > 0 and residential_score < 10: residential_score = 15

    vibe.party_score = round(party_score, 1)
    vibe.study_score = round(study_score, 1)
    vibe.shopping_score = round(shopping_score, 1)
    vibe.residential_score = round(residential_score, 1)
    
    vibe.save()
    return vibe
