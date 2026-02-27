from django.shortcuts import render
from property.models import Property

def fullscreen_map(request):
    """View for full screen map showing all/selected properties."""
    properties = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return render(request, 'map/fullscreen_map.html', {
        'properties': properties
    })
