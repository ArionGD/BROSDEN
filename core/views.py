from django.shortcuts import render

def index(request):
    context = {
        'home_stats': [
            {'value': "12,000+", 'label': "Properties"},
            {'value': "98%", 'label': "Verified Listings"},
            {'value': "India's", 'label': "Top 10 Cities"},
            {'value': "4.9★", 'label': "Average Rating"}
        ],
        'home_features': [
            {'icon': 'fa-shield-halved', 'title': 'Secured Transactions', 'desc': 'Every property undergoes 45 verification checks before listing.', 'color': 'arion-orange'},
            {'icon': 'fa-bolt', 'title': 'AI-Powered Matching', 'desc': 'Our engine matches your lifestyle to ideal units in under 60 seconds.', 'color': 'arion-blue'},
            {'icon': 'fa-headset', 'title': '24/7 Concierge', 'desc': 'Dedicated managers guide you from document signing to possession.', 'color': 'arion-orange'}
        ],
        'categories': [
            {'name': 'Apartments', 'icon': 'fa-building'},
            {'name': 'Villas', 'icon': 'fa-house-chimney'},
            {'name': 'Commercial', 'icon': 'fa-shop'},
            {'name': 'Plots', 'icon': 'fa-map'}
        ],
        'featured_properties': [
            {'name': 'Skyview Premium', 'price': '₹ 85.5 L', 'loc': 'Jubilee Hills, Hyderabad', 'beds': '3 BHK', 'size': '1.8k sqft'},
            {'name': 'Marine Luxury Villa', 'price': '₹ 1.2 Cr', 'loc': 'Banjara Hills, Hyderabad', 'beds': '4 BHK', 'size': '2.5k sqft'},
            {'name': 'Suburban Family Home', 'price': '₹ 45.0 L', 'loc': 'Gachibowli, Hyderabad', 'beds': '2 BHK', 'size': '1.2k sqft'}
        ],
        'testimonials': [
            {
                'name': 'Arjun Sharma',
                'role': 'Software Engineer, Amazon',
                'text': 'Transparent process and zero brokerage actually meant zero hidden costs. Highly recommend for working professionals.',
                'color': 'arion-blue'
            },
            {
                'name': 'Priya Reddy',
                'role': 'Property Owner, Gachibowli',
                'text': 'My rental income increased 15% after listing with Arion. The KYC process for tenants is incredibly thorough.',
                'color': 'arion-orange'
            }
        ]
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
