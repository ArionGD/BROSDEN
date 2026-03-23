from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import KYC
from .models import UserDocument, DocumentType

@receiver(post_save, sender=KYC)
def sync_kyc_to_dms(sender, instance, **kwargs):
    """Automatically sync newly uploaded KYC documents to the DMS Document Vault."""
    user = instance.user
    
    # 1. Identity Proof (Common for both)
    if instance.id_type == 'AADHAAR' and instance.aadhaar_image:
        UserDocument.objects.get_or_create(
            user=user,
            doc_type=DocumentType.ID_PROOF,
            file=instance.aadhaar_image,
            defaults={'title': 'Aadhaar Card (via KYC)'}
        )
    elif instance.id_type == 'PAN' and instance.pan_image:
        UserDocument.objects.get_or_create(
            user=user,
            doc_type=DocumentType.ID_PROOF,
            file=instance.pan_image,
            defaults={'title': 'PAN Card (via KYC)'}
        )
    
    # 2. Passport Photo
    if instance.passport_photo:
        UserDocument.objects.get_or_create(
            user=user,
            doc_type=DocumentType.OTHER,
            file=instance.passport_photo,
            defaults={'title': 'Passport Size Photo (via KYC)'}
        )

    # 3. Ownership Proof (Owners only)
    if instance.ownership_proof:
        UserDocument.objects.get_or_create(
            user=user,
            doc_type=DocumentType.PROPERTY_PAPER,
            file=instance.ownership_proof,
            defaults={'title': 'Electricity Bill / Ownership Proof (via KYC)'}
        )

    # 4. Property Tax Receipt (Owners only)
    if instance.property_tax_receipt:
        UserDocument.objects.get_or_create(
            user=user,
            doc_type=DocumentType.TAX_DOC,
            file=instance.property_tax_receipt,
            defaults={'title': 'Property Tax Receipt (via KYC)'}
        )
