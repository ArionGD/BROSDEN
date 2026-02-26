from django.shortcuts import render
from django.db.models import Count, Sum
from property.models import Property
from booking.models import BookingRequest
from .models import PropertyView, SearchActivity
from accounts.decorators import tenant_required, owner_required

@owner_required
def owner_analytics(request):
    """Analytics for Owners: Property performance and revenue trends."""
    user_properties = Property.objects.filter(owner=request.user)
    total_properties = user_properties.count()
    
    # Booking Stats
    bookings = BookingRequest.objects.filter(property__owner=request.user)
    total_requests = bookings.count()
    approved_requests = bookings.filter(status='APPROVED').count()
    pending_requests = bookings.filter(status='PENDING').count()
    
    rejected_requests = bookings.filter(status='REJECTED').count()
    
    # Revenue (Estimate from approved properties prices)
    projected_revenue = user_properties.aggregate(Sum('price'))['price__sum'] or 0
    actual_revenue = bookings.filter(status='APPROVED').aggregate(Sum('property__price'))['property__price__sum'] or 0
    
    # Views per property
    views_query = PropertyView.objects.filter(property__owner=request.user).values('property__title').annotate(total_views=Count('id')).order_by('-total_views')[:5]
    views_data = list(views_query)
    max_views = max([v['total_views'] for v in views_data]) if views_data else 1
    
    for v in views_data:
        v['percentage'] = (v['total_views'] / max_views * 100) if max_views > 0 else 0

    context = {
        'total_properties': total_properties,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'pending_requests': pending_requests,
        'rejected_requests': rejected_requests,
        'actual_revenue': actual_revenue,
        'projected_revenue': projected_revenue,
        'views_data': views_data,
        'max_views': max_views,
    }
    return render(request, 'analytics/owner_dashboard.html', context)

@tenant_required
def tenant_analytics(request):
    """Analytics for Tenants: Search history and booking success."""
    my_bookings = BookingRequest.objects.filter(tenant=request.user)
    total_sent = my_bookings.count()
    approved = my_bookings.filter(status='APPROVED').count()
    rejected = my_bookings.filter(status='REJECTED').count()
    
    # Success Rate
    success_rate = (approved / total_sent * 100) if total_sent > 0 else 0
    
    # Search Activity
    recent_searches = SearchActivity.objects.filter(user=request.user).order_by('-searched_at')[:5]

    context = {
        'total_sent': total_sent,
        'approved': approved,
        'rejected': rejected,
        'success_rate': round(success_rate, 1),
        'recent_searches': recent_searches,
    }
    return render(request, 'analytics/tenant_dashboard.html', context)
