from django.shortcuts import render
from property.models import Property
from accounts.models import User
from booking.models import BookingRequest

def index(request):
    """Main Home Page with Spatial Discovery Engine."""
    context = {
        'home_stats': [
            {'value': f"{Property.objects.count():,}", 'label': "Verified Listings", 'icon': 'fa-plus'},
            {'value': f"{User.objects.filter(role='OWNER').count():,}", 'label': "Trusted Owners", 'icon': 'fa-shield-halved'},
            {'value': f"{BookingRequest.objects.filter(status='PAID').count():,}", 'label': "Happy Tenants", 'icon': 'fa-heart'},
            {'value': "4.7", 'label': "Avg Reviews", 'icon': 'fa-star'}
        ],
        'home_features': [
            {'icon': 'fa-shield-halved', 'title': 'Secured Transactions', 'desc': 'Every property undergoes 45 verification checks before listing.', 'color': 'arion-orange'},
            {'icon': 'fa-bolt', 'title': 'AI-Powered Matching', 'desc': 'Our engine matches your lifestyle to ideal units in under 60 seconds.', 'color': 'arion-blue'},
            {'icon': 'fa-headset', 'title': '24/7 Concierge', 'desc': 'Dedicated managers guide you from document signing to possession.', 'color': 'arion-orange'}
        ],
        'categories': [
            {'name': 'Apartments', 'icon': 'fa-building'},
            {'name': 'PG Accommodations', 'icon': 'fa-hotel'},
            {'name': 'Student Hostels', 'icon': 'fa-user-graduate'},
            {'name': 'Shared Living', 'icon': 'fa-users'}
        ],
        'featured_properties': [
            {'name': 'Skyview Premium', 'price': '₹ 85.5 L', 'loc': 'Jubilee Hills, Hyderabad', 'beds': '3 BHK', 'size': '1.8k sqft', 'icon': 'fa-building'},
            {'name': 'Marine Luxury Villa', 'price': '₹ 1.2 Cr', 'loc': 'Banjara Hills, Hyderabad', 'beds': '4 BHK', 'size': '2.5k sqft', 'icon': 'fa-hotel'},
            {'name': 'Suburban Family Home', 'price': '₹ 45.0 L', 'loc': 'Gachibowli, Hyderabad', 'beds': '2 BHK', 'size': '1.2k sqft', 'icon': 'fa-house-user'}
        ],
        'testimonials': [
            {
                'name': 'anuj xxx',
                'role': 'XXX, Ahmedabad',
                'text': 'Transparent process and zero brokerage actually meant zero hidden costs. Highly recommend for working professionals.',
                'color': 'arion-blue'
            },
            {
                'name': 'dinesh xxx',
                'role': 'XXX, Ahmedabad',
                'text': 'Finding a high-quality apartment was so much easier with BrosDen. The digital documentation saved me so much time.',
                'color': 'arion-orange'
            }
        ],
        'map_properties': Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)[:20],
        'localities': ['Gota', 'Naranpura', 'Navrangpura', 'Satellite', 'Chandlodiya', 'Ghatlodiya', 'Naanpura', 'Bodhakdev']
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
