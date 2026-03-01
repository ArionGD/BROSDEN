from django.db import models
from django.conf import settings
from property.models import Property

class BookingRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tenant_bookings')
    message = models.TextField(blank=True, help_text="Message to the owner")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateField(null=True, blank=True, help_text="Tenancy start date (always 1st of the month)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.username} - {self.property.title} ({self.status})"

    class Meta:
        ordering = ['-created_at']
