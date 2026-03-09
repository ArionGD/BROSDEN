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
    
    # Common Fields (Required for Both)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    availability_date = models.DateField(null=True, blank=True)
    security_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Existing compatibility (can be used for calculations)
    security_deposit_months = models.IntegerField(default=2, help_text="Number of months of rent for security deposit")
    contract_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Percentage of security deposit for contract fee")
    
    # 2. Flat / Apartment Specific Fields
    BHK_CHOICES = (
        ('1BHK', '1BHK'),
        ('2BHK', '2BHK'),
        ('3BHK', '3BHK'),
        ('4BHK+', '4BHK+'),
    )
    FURNISHING_CHOICES = (
        ('FULLY', 'Fully Furnished'),
        ('SEMI', 'Semi-Furnished'),
        ('UNFURNISHED', 'Unfurnished'),
    )
    PARKING_CHOICES = (
        ('COVERED', 'Covered (Basement)'),
        ('OPEN', 'Open Parking'),
    )
    
    bhk_type = models.CharField(max_length=10, choices=BHK_CHOICES, null=True, blank=True)
    floor_number = models.IntegerField(null=True, blank=True)
    total_floors = models.IntegerField(null=True, blank=True)
    furnishing_status = models.CharField(max_length=20, choices=FURNISHING_CHOICES, null=True, blank=True)
    balconies = models.IntegerField(default=0)
    parking_type = models.CharField(max_length=20, choices=PARKING_CHOICES, null=True, blank=True)
    maintenance_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amenities = models.TextField(blank=True, help_text="List amenities (Lift, Gym, etc.)")
    
    # 3. PG / Room Specific Fields
    SHARING_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('TRIPLE', 'Triple'),
        ('QUADRUPLE', 'Quadruple'),
    )
    GENDER_CHOICES = (
        ('BOYS', 'Boys Only'),
        ('GIRLS', 'Girls Only'),
        ('COED', 'Co-ed'),
    )
    
    sharing_type = models.CharField(max_length=20, choices=SHARING_CHOICES, null=True, blank=True)
    gender_preference = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    food_included = models.BooleanField(default=False)
    food_details = models.TextField(blank=True, help_text="Specify meals: Breakfast, Lunch, Dinner")
    ac_available = models.BooleanField(default=False)
    laundry_available = models.BooleanField(default=False)
    wifi_available = models.BooleanField(default=False)
    rules_restrictions = models.TextField(blank=True, help_text="Curfew, Guest policy, etc.")
    cleaning_frequency = models.CharField(max_length=100, blank=True)
    
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
        # Use the explicit security_deposit if set, otherwise fallback to months-based logic
        deposit = self.security_deposit if self.security_deposit > 0 else (self.price * self.security_deposit_months)
        contract_fee = 2000  # Fixed fee as requested
        total = float(deposit) + contract_fee
        return {
            'monthly_rent': self.price,
            'security_deposit': deposit,
            'security_months': self.security_deposit_months,
            'contract_fee': contract_fee,
            'contract_percentage': self.contract_fee_percentage,
            'total': total
        }

    class Meta:
        verbose_name_plural = "Properties"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"
