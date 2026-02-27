from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Wishlist
from property.models import Property

@login_required
def toggle_wishlist(request, property_id):
    """Toggle a property in the user's wishlist via AJAX or POST."""
    if request.user.role != 'TENANT':
        return JsonResponse({'status': 'error', 'message': 'Only tenants can wishlist properties.'}, status=403)
    
    prop = get_object_or_404(Property, id=property_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, property=prop)

    if wishlist_item.exists():
        wishlist_item.delete()
        added = False
        message = "Removed from wishlist"
    else:
        Wishlist.objects.create(user=request.user, property=prop)
        added = True
        message = "Added to wishlist"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'added': added, 'message': message})
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'tenant:dashboard'))

@login_required
def wishlist_list(request):
    """Display the tenant's wishlist."""
    if request.user.role != 'TENANT':
        messages.error(request, "Only tenants can access the wishlist.")
        return redirect('index')
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('property', 'property__owner')
    
    return render(request, 'wishlist/wishlist_list.html', {
        'wishlist_items': wishlist_items,
        'portal_base': 'tenant/portal_base.html'
    })
