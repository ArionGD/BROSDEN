from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Contract

@login_required
def view_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check if user is tenant or owner of the booking
    if request.user != contract.booking.tenant and request.user != contract.booking.property.owner:
        return render(request, '403.html', status=403)
        
    return render(request, 'contract/view_contract.html', {'contract': contract})
