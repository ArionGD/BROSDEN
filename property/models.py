from django.db import models
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPES = (
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('VILLA', 'Villa'),
        ('COMMERCIAL', 'Commercial'),
        ('PLOT', 'Plot'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='APARTMENT')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    sqft = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Properties"
