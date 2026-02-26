from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Contract
from payment.models import PaymentReceipt

@login_required
def view_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user != contract.booking.tenant and request.user != contract.booking.property.owner:
        return render(request, '403.html', status=403)
    return render(request, 'contract/view_contract.html', {'contract': contract})

@login_required
def view_deposit_receipt(request, receipt_id):
    """Specific receipt for the Security Deposit payment."""
    receipt = get_object_or_404(PaymentReceipt, id=receipt_id, user=request.user)
    return render(request, 'contract/receipt_deposit.html', {'receipt': receipt})

@login_required
def view_contract_receipt(request, contract_id):
    """Specific receipt (acknowledgment) for the Contract execution."""
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user != contract.booking.tenant and request.user != contract.booking.property.owner:
        return render(request, '403.html', status=403)
    return render(request, 'contract/receipt_contract.html', {'contract': contract})
