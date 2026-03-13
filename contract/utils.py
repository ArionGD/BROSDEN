from .models import Contract, ContractTemplate
from django.utils import timezone

def generate_contract(booking):
    template = ContractTemplate.objects.filter(is_active=True).first()
    if not template:
        # Fallback professional template
        template_content = """RESIDENTIAL LEASE AGREEMENT

This Residential Lease Agreement ("Agreement") is entered into on {start_date}, between:

LANDLORD: {owner_name} (the "Landlord")
AND
TENANT: {tenant_name} (the "Tenant")

1. PROPERTY: The Landlord agrees to lease the residential property located at {property_title} to the Tenant.

2. TERM: This lease shall commence on {start_date} and shall continue for a primary term of 12 months.

3. RENT: The monthly rent for the Property is ₹{monthly_rent}, payable in advance on the 1st day of each month.

4. SECURITY DEPOSIT: Upon execution of this Agreement, the Tenant has paid a Security Deposit of ₹{amount}. The deposit shall be held as security for the performance of the Tenant's obligations and returned upon termination of the lease, subject to deductions for damages or unpaid dues.

5. CONTRACT FEE: A one-time non-refundable facilitation fee of ₹{contract_fee} has been paid towards the execution of this digital contract.

6. MAINTENANCE AND REPAIRS: The Tenant shall maintain the Property in a clean and sanitary condition. Any major repairs required due to normal wear and tear shall be the Landlord's responsibility, while minor repairs or damages caused by the Tenant's negligence shall be borne by the Tenant.

7. UTILITIES: The Tenant is responsible for all utility payments including electricity, water, and internet unless otherwise specified.

8. TERMINATION: Either party may terminate this agreement by providing a 30-day written notice.

This document is digitally executed and holds legal validity under the Information Technology Act.

Total Amount Paid during execution: ₹{total_paid} (Security Deposit + Contract Fee).
"""
    else:
        template_content = template.content

    # Calculate Breakdown
    breakdown = booking.property.get_financial_breakdown()

    # Replace placeholders
    rendered_content = template_content.format(
        owner_name=booking.property.owner.username,
        tenant_name=booking.tenant.username,
        property_title=booking.property.title,
        amount=breakdown['security_deposit'],
        contract_fee=breakdown['contract_fee'],
        total_paid=breakdown['total'],
        monthly_rent=breakdown['monthly_rent'],
        start_date=booking.created_at.strftime('%B %d, %Y')
    )

    contract, created = Contract.objects.get_or_create(
        booking=booking,
        defaults={
            'template': template,
            'content': rendered_content
        }
    )
    return contract
