from django.db import models
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPES = (
        ('APARTMENT', 'Apartment'),
        ('PG', 'Paying Guest'),
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
    
    # Financial Settings
    security_deposit_months = models.IntegerField(default=2, help_text="Number of months of rent for security deposit")
    contract_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Percentage of security deposit for contract fee")
    
    is_verified = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # PG / Capacity tracking
    total_capacity = models.IntegerField(default=1, help_text="Total number of tenants this property can handle")
    current_occupancy = models.IntegerField(default=0, help_text="Number of current tenants")

    @property
    def available_spaces(self):
        return max(0, self.total_capacity - self.current_occupancy)

    @property
    def is_vacant(self):
        return self.available_spaces > 0

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_financial_breakdown(self):
        """Returns a dictionary with security deposit, contract fee and total."""
        security_deposit = self.price * self.security_deposit_months
        contract_fee = (security_deposit * self.contract_fee_percentage) / 100
        total = security_deposit + contract_fee
        return {
            'monthly_rent': self.price,
            'security_deposit': security_deposit,
            'security_months': self.security_deposit_months,
            'contract_fee': contract_fee,
            'contract_percentage': self.contract_fee_percentage,
            'total': total
        }

    class Meta:
        verbose_name_plural = "Properties"
