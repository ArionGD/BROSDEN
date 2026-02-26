from django.db import models
from django.conf import settings
from booking.models import BookingRequest

class ContractTemplate(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField(help_text="Use placeholders like {tenant_name}, {owner_name}, {property_title}, {amount}")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contract(models.Model):
    booking = models.OneToOneField(BookingRequest, on_delete=models.CASCADE, related_name='contract')
    template = models.ForeignKey(ContractTemplate, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_signed_by_tenant = models.BooleanField(default=False)
    is_signed_by_owner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Contract for {self.booking.property.title} - {self.booking.tenant.username}"
