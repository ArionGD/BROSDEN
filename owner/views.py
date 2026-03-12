from django.shortcuts import render
from accounts.decorators import owner_required
from payment.models import PaymentReceipt
from django.db.models import Count, Sum

@owner_required
def dashboard(request):
    from property.models import Property
    from booking.models import BookingRequest
    from analytics.models import PropertyView

    user_properties = Property.objects.filter(owner=request.user)
    total_properties = user_properties.count()
    
    bookings = BookingRequest.objects.filter(property__owner=request.user)
    total_requests = bookings.count()
    approved_requests = bookings.filter(status='APPROVED').count()
    pending_requests = bookings.filter(status='PENDING').count()
    rejected_requests = bookings.filter(status='REJECTED').count()
    
    projected_revenue = user_properties.aggregate(Sum('price'))['price__sum'] or 0
    actual_revenue = bookings.filter(status='APPROVED').aggregate(Sum('property__price'))['property__price__sum'] or 0
    
    total_rent_collected = PaymentReceipt.objects.filter(
        booking__property__owner=request.user,
        payment_type='RENT'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    from django.db.models.functions import TruncMonth
    from django.utils import timezone
    import datetime

    monthly_income = PaymentReceipt.objects.filter(
        booking__property__owner=request.user,
        payment_type='RENT'
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('amount')).order_by('month')
    
    income_labels = [m['month'].strftime('%b %Y') for m in monthly_income]
    income_values = [float(m['total']) for m in monthly_income]

    if not income_values:
        income_labels = []
        income_values = []
        today = timezone.now().date()
        for i in range(5, -1, -1):
            month_date = today - datetime.timedelta(days=30*i)
            income_labels.append(month_date.strftime('%b %Y'))
            income_values.append(0)

    occupied = user_properties.filter(current_occupancy__gt=0).count()
    vacant = user_properties.filter(current_occupancy=0).count()

    views_query = PropertyView.objects.filter(property__owner=request.user).values('property__title').annotate(total_views=Count('id')).order_by('-total_views')[:5]
    views_data = list(views_query)
    max_views = max([v['total_views'] for v in views_data]) if views_data else 1
    
    for v in views_data:
        v['percentage'] = (v['total_views'] / max_views * 100) if max_views > 0 else 0

    view_labels = [v['property__title'] for v in views_data]
    view_counts = [v['total_views'] for v in views_data]

    if not view_counts and total_properties > 0:
        view_labels = [p.title for p in user_properties[:5]]
        view_counts = [0] * len(view_labels)
    elif not view_counts:
        view_labels = ['No Properties Yet']
        view_counts = [0]

    context = {
        'total_properties': total_properties,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'pending_requests': pending_requests,
        'rejected_requests': rejected_requests,
        'actual_revenue': actual_revenue,
        'projected_revenue': projected_revenue,
        'total_rent_collected': total_rent_collected,
        'views_data': views_data,
        'max_views': max_views,
        'view_labels': view_labels,
        'view_counts': view_counts,
        'income_labels': income_labels,
        'income_values': income_values,
        'occupied_count': occupied,
        'vacant_count': vacant,
    }
    return render(request, 'owner/dashboard.html', context)

@owner_required
def rent_received(request):
    # Fetch all rent receipts for properties owned by this user
    rent_payments = PaymentReceipt.objects.filter(
        booking__property__owner=request.user,
        payment_type='RENT'
    ).order_by('-created_at')
    
    context = {
        'rent_payments': rent_payments,
    }
    return render(request, 'owner/rent_received.html', context)
