from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Contract
from payment.models import PaymentReceipt


def _check_contract_access(user, contract):
    """Shared access guard: only tenant or property owner may view."""
    return user == contract.booking.tenant or user == contract.booking.property.owner


@login_required
def view_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if not _check_contract_access(request.user, contract):
        return render(request, '403.html', status=403)
    return render(request, 'contract/view_contract.html', {'contract': contract})


@login_required
def view_deposit_receipt(request, receipt_id):
    """Dedicated receipt for the Security Deposit payment."""
    receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
    if not (request.user == receipt.user or request.user == receipt.booking.property.owner):
        return render(request, '403.html', status=403)
        
    return render(request, 'contract/view_deposit.html', {
        'receipt': receipt,
        'portal_base': request.user.portal_base
    })


@login_required
def view_contract_receipt(request, contract_id):
    """Acknowledgment receipt for the Contract execution."""
    contract = get_object_or_404(Contract, id=contract_id)
    if not _check_contract_access(request.user, contract):
        return render(request, '403.html', status=403)
    return render(request, 'contract/receipt_contract.html', {'contract': contract})
