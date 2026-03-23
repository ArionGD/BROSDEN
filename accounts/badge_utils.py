from django.db.models import Avg
from reviews.models import PropertyReview

def get_owner_badge(owner):
    if not owner or not hasattr(owner, 'is_authenticated') or not owner.is_authenticated:
        return {'color': 'white', 'name': 'No Reviews', 'avg': 0.0, 'icon': 'fa-solid fa-circle'}

    """
    Returns the badge color and average rating for a given owner based on reviews.
    - Avg > 4.5 -> Diamond
    - Avg > 4.0 -> Gold
    - Avg > 3.5 -> Silver
    - Avg >= 2.0 -> Orange
    - Avg < 2.0 -> Red
    - No reviews -> White
    """
    reviews = PropertyReview.objects.filter(property__owner=owner)
    
    if not reviews.exists():
        return {'color': 'white', 'name': 'No Reviews', 'avg': 0.0, 'icon': 'fa-solid fa-circle'}
    
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating is None:
        return {'color': 'white', 'name': 'No Reviews', 'avg': 0.0, 'icon': 'fa-solid fa-circle'}
        
    avg_rating = round(float(avg_rating), 2)
    
    if avg_rating > 4.5:
        return {'color': 'cyan', 'name': 'Diamond', 'avg': avg_rating, 'icon': 'fa-solid fa-gem'}
    elif avg_rating > 4.0:
        return {'color': 'amber', 'name': 'Gold', 'avg': avg_rating, 'icon': 'fa-solid fa-medal'}
    elif avg_rating > 3.5:
        return {'color': 'slate', 'name': 'Silver', 'avg': avg_rating, 'icon': 'fa-solid fa-award'}
    elif avg_rating >= 2.0:
        return {'color': 'orange', 'name': 'Bronze', 'avg': avg_rating, 'icon': 'fa-solid fa-star'}
    else:
        return {'color': 'red', 'name': 'Needs Improvement', 'avg': avg_rating, 'icon': 'fa-solid fa-triangle-exclamation'}
