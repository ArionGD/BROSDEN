from .models import Contract, ContractTemplate
from django.utils import timezone

def generate_contract(booking):
    template = ContractTemplate.objects.filter(is_active=True).first()
    if not template:
        # Fallback basic template
        template_content = "This is a contract between {owner_name} and {tenant_name} for the property {property_title}. Security Deposit: {amount}."
    else:
        template_content = template.content

    # Replace placeholders
    rendered_content = template_content.format(
        owner_name=booking.property.owner.username,
        tenant_name=booking.tenant.username,
        property_title=booking.property.title,
        amount=booking.property.price
    )

    contract, created = Contract.objects.get_or_create(
        booking=booking,
        defaults={
            'template': template,
            'content': rendered_content
        }
    )
    return contract
