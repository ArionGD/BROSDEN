from .models import ProMembership

def get_user_tier(user):
    """Utility to get a user's current membership tier data."""
    if not user.is_authenticated:
        return 'NORMAL'
    
    membership = getattr(user, 'pro_membership', None)
    if membership and membership.is_active:
        return membership.tier
    return 'NORMAL'

def get_tier_color(tier):
    """Returns aesthetic color codes based on tier."""
    colors = {
        'NORMAL': 'slate',
        'PRO': 'arion-blue',
        'GOLD': 'arion-orange'
    }
    return colors.get(tier, 'slate')

def has_premium_feature(user, feature_name):
    """
    Check if a user has access to a specific premium feature.
    Placeholder for more complex plan-based logic.
    """
    tier = get_user_tier(user)
    if tier == 'GOLD':
        return True
    if tier == 'PRO':
        # Define features allowed for PRO but not NORMAL
        pro_features = ['priority_search', 'limit_featured_5', 'featured_badge']
        return feature_name in pro_features
    return False
