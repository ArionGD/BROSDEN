from django.shortcuts import render
from property.models import Property

def fullscreen_map(request):
    """View for full screen map showing all/selected properties."""
    focus_id = request.GET.get('focus')
    properties = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    # Determine base template based on role
    base_template = 'tenant/portal_base.html' if request.user.role == 'TENANT' else 'owner/portal_base.html'
    
    return render(request, 'map/fullscreen_map.html', {
        'properties': properties,
        'focus_id': focus_id,
        'base_template': base_template
    })
