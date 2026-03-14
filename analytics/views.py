from django.shortcuts import render
from django.db.models import Count, Sum, Q
from property.models import Property
from booking.models import BookingRequest
from payment.models import PaymentReceipt
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
    
    # Actual Rent Collected (From PaymentReceipts)
    total_rent_collected = PaymentReceipt.objects.filter(
        booking__property__owner=request.user,
        payment_type='RENT'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Monthly Income Trends (Last 6 Months)
    from django.db.models.functions import TruncMonth
    from django.utils import timezone
    import datetime

    monthly_income = PaymentReceipt.objects.filter(
        booking__property__owner=request.user,
        payment_type='RENT'
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('amount')).order_by('month')
    
    income_labels = [m['month'].strftime('%b %Y') for m in monthly_income]
    income_values = [float(m['total']) for m in monthly_income]

    # Provide real 6 months of 0s if empty
    if not income_values:
        income_labels = []
        income_values = []
        today = timezone.now().date()
        for i in range(5, -1, -1):
            month_date = today - datetime.timedelta(days=30*i)
            income_labels.append(month_date.strftime('%b %Y'))
            income_values.append(0)

    # Occupancy Stats for 360 degree chart
    occupied = user_properties.filter(current_occupancy__gt=0).count()
    vacant = user_properties.filter(current_occupancy=0).count()

    # Views per property (Top 5)
    views_query = PropertyView.objects.filter(property__owner=request.user).values('property__title').annotate(total_views=Count('id')).order_by('-total_views')[:5]
    views_data = list(views_query)
    
    view_labels = [v['property__title'] for v in views_data]
    view_counts = [v['total_views'] for v in views_data]

    # If no views yet, use actual properties with 0 views
    if not view_counts and total_properties > 0:
        view_labels = [p.title for p in user_properties[:5]]
        view_counts = [0] * len(view_labels)
    elif not view_counts:
        view_labels = ['No Properties Yet']
        view_counts = [0]

    context = {
        'total_properties': total_properties,
        'total_requests': total_requests,
        'approved_requests': approved_requests or 0,
        'pending_requests': pending_requests or 0,
        'rejected_requests': rejected_requests or 0,
        'actual_revenue': actual_revenue,
        'projected_revenue': projected_revenue,
        'total_rent_collected': total_rent_collected,
        'views_data': views_data,
        'view_labels': view_labels,
        'view_counts': view_counts,
        'income_labels': income_labels,
        'income_values': income_values,
        'occupied_count': occupied,
        'vacant_count': vacant,
    }
    return render(request, 'analytics/owner_dashboard.html', context)

@tenant_required
def tenant_analytics(request):
    """Analytics for Tenants: Financial standing, maintenance, and legal vault."""
    from contract.models import RentSchedule, Contract
    from helpdesk.models import Ticket
    from payment.models import PaymentReceipt
    
    my_bookings = BookingRequest.objects.filter(tenant=request.user)
    total_sent = my_bookings.count()
    approved = my_bookings.filter(status='APPROVED').count()
    rejected = my_bookings.filter(status='REJECTED').count()
    
    # Success Rate
    success_rate = (approved / total_sent * 100) if total_sent > 0 else 0
    
    # Financial Overview
    rents = RentSchedule.objects.filter(contract__booking__tenant=request.user)
    total_paid = rents.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
    next_payment = rents.filter(status__in=['UNPAID', 'OVERDUE']).order_by('due_date').first()
    last_payment = rents.filter(status='PAID').order_by('-paid_at').first()

    # Timeline Logic
    from django.utils import timezone
    from datetime import date
    today = date.today()
    
    # Get payments for timeline: Previous, Current, Next
    timeline = {
        'prev': rents.filter(due_date__month=(today.month-2)%12 or 12).first(),
        'current': rents.filter(due_date__month=today.month, due_date__year=today.year).first(),
        'next': rents.filter(due_date__month=(today.month)%12 + 1).first()
    }

    # Price Breakup for Next Payment
    breakup = None
    if next_payment:
        breakup = {
            'base': next_payment.amount,
            'tax': float(next_payment.amount) * 0.05, # Example 5% GST/Service tax
            'total': float(next_payment.amount) * 1.05
        }
    
    # Maintenance & Ledger
    active_tickets = Ticket.objects.filter(user=request.user, status__in=['OPEN', 'IN_PROGRESS'])
    recent_tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')[:3]
    payment_ledger = PaymentReceipt.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Current Residence & KYC
    active_contract = Contract.objects.filter(booking__tenant=request.user, is_signed_by_tenant=True, is_signed_by_owner=True).first()
    kyc_profile = getattr(request.user, 'kyc', None)
    latest_booking = my_bookings.first()

    # Search Activity
    recent_searches = SearchActivity.objects.filter(user=request.user).order_by('-searched_at')[:5]

    # Recommendations (Based on last search city)
    last_search = recent_searches.first()
    recommendations = Property.objects.none()
    if last_search and last_search.query:
        # Try to match city from query
        recommendations = Property.objects.filter(
            Q(city__icontains=last_search.query) | 
            Q(title__icontains=last_search.query)
        ).exclude(id__in=my_bookings.values_list('property_id', flat=True))[:3]

    context = {
        'total_sent': total_sent,
        'approved': approved,
        'rejected': rejected,
        'latest_booking': latest_booking,
        'success_rate': round(success_rate, 1),
        'total_paid': total_paid,
        'next_payment': next_payment,
        'last_payment': last_payment,
        'active_contract': active_contract,
        'recent_searches': recent_searches,
        'recommendations': recommendations,
        'timeline': timeline,
        'breakup': breakup,
        'active_tickets': active_tickets,
        'recent_tickets': recent_tickets,
        'payment_ledger': payment_ledger,
        'kyc_profile': kyc_profile,
        'auto_pay_enabled': False, # Simulation for now
        'credit_reporting': False, # Simulation for now
    }
    return render(request, 'analytics/tenant_dashboard.html', context)



