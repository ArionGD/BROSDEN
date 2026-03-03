from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from property.models import Property
from .services import calculate_property_vibe
from .models import PropertyVibe

def calculate_vibe(request, property_id):
    """
    API endpoint to trigger vibe calculation or return existing vibe scores.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    prop = get_object_or_404(Property, pk=property_id)
    
    # Try to get existing vibe if it exists
    force = request.GET.get('force') == 'true'
    
    # Trigger the calculation via service
    vibe = calculate_property_vibe(prop, force=force)
    
    if not vibe:
        return JsonResponse({
            'success': False,
            'message': 'Cannot calculate vibe. Property might be missing coordinates or API failed.'
        }, status=400)
        
    return JsonResponse({
        'success': True,
        'scores': {
            'party': vibe.party_score,
            'study': vibe.study_score,
            'shopping': vibe.shopping_score,
            'residential': vibe.residential_score
        },
        'top_vibe': vibe.top_vibe,
        'last_updated': vibe.last_updated.isoformat()
    })
