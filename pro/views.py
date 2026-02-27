from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import owner_required
from .models import ProMembership

@owner_required
def pro_landing(request):
    """View to show pro membership options to owners."""
    membership = ProMembership.objects.filter(user=request.user).first()
    
    return render(request, 'pro/landing.html', {
        'membership': membership,
        'portal_base': 'owner/portal_base.html'
    })

@owner_required
def upgrade_tier(request, tier):
    """Placeholder view to handle upgrade requests."""
    if tier not in ['PRO', 'GOLD']:
        messages.error(request, "Invalid membership tier.")
        return redirect('pro:landing')
        
    # In a real app, this would redirect to payment
    messages.success(request, f"Redirecting to payment for {tier} Pro Membership...")
    return redirect('pro:landing')
