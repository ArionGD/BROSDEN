from django.db import models
from django.conf import settings
from property.models import Property
from django.core.validators import MinValueValidator, MaxValueValidator

class PropertyReview(models.Model):
    """Review written by a Tenant about a Property they stayed in."""
    booking = models.OneToOneField('booking.BookingRequest', on_delete=models.CASCADE, related_name='property_review')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_reviews')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_property_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tenant {self.tenant.username} -> {self.property.title} ({self.rating} stars)"

class TenantReview(models.Model):
    """Review written by an Owner about a Tenant who stayed in their property."""
    booking = models.OneToOneField('booking.BookingRequest', on_delete=models.CASCADE, related_name='tenant_review')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_tenant_reviews')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_tenant_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Owner {self.owner.username} -> {self.tenant.username} ({self.rating} stars)"
