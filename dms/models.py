from django.db import models
from django.conf import settings

class DocumentType(models.TextChoices):
    SALARY_SLIP = 'SALARY_SLIP', 'Salary Slip'
    PREVIOUS_LEASE = 'PREVIOUS_LEASE', 'Previous Lease Agreement'
    EMPLOYMENT_LETTER = 'EMPLOYMENT_LETTER', 'Employment Letter'
    BANK_STATEMENT = 'BANK_STATEMENT', 'Bank Statement'
    ID_PROOF = 'ID_PROOF', 'Government ID Proof'
    PROPERTY_PAPER = 'PROPERTY_PAPER', 'Property Ownership Document'
    TAX_DOC = 'TAX_DOC', 'Tax Document/Receipt'
    OTHER = 'OTHER', 'Other Document'

class UserDocument(models.Model):
    """General Document Vault for all users (Owners and Tenants)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=50, choices=DocumentType.choices, default=DocumentType.OTHER)
    title = models.CharField(max_length=255, help_text="A friendly name for the document")
    file = models.FileField(upload_to='user_docs/%Y/%m/%d/')
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_doc_type_display()} ({self.title})"
