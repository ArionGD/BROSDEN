from django.db import models
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPES = (
        ('APARTMENT', 'Apartment / Flat'),
        ('PG', 'PG / Hostel'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    unit_number = models.CharField(max_length=50, blank=True, help_text="Flat/Unit Number (Required for Legal Agreement)")
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='APARTMENT')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    total_capacity = models.PositiveIntegerField(default=1, help_text="Total number of tenants this property can handle") # Moved from bottom
    bed_count = models.PositiveIntegerField(default=1, help_text="Specific for PG/Hostel sharing count")
    sqft = models.PositiveIntegerField(null=True, blank=True) # Changed from IntegerField(default=0)
    
    # Common Fields (Required for Both)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    available_from = models.DateField(null=True, blank=True)
    security_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Financials & Legal
    electricity_included = models.BooleanField(default=False)
    water_included = models.BooleanField(default=False)
    maintenance_included = models.BooleanField(default=True)
    wifi_included = models.BooleanField(default=False)
    lock_in_period = models.IntegerField(default=0, help_text="Months")
    notice_period = models.IntegerField(default=30, help_text="Days")
    electricity_bill = models.FileField(upload_to='property/verification/electricity/', null=True, blank=True)
    property_tax_slip = models.FileField(upload_to='property/verification/tax/', null=True, blank=True)
    
    # Existing compatibility
    security_deposit_months = models.IntegerField(default=2)
    contract_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    
    # 2. Flat / Apartment Specific Fields
    FURNISHING_CHOICES = (
        ('FULLY', 'Fully Furnished'),
        ('SEMI', 'Semi-Furnished'),
        ('UNFURNISHED', 'Unfurnished'),
    )
    PARKING_CHOICES = (
        ('COVERED', 'Covered (Basement)'),
        ('OPEN', 'Open Parking'),
    )
    
    furnishing_status = models.CharField(max_length=20, choices=FURNISHING_CHOICES, null=True, blank=True)
    floor_number = models.IntegerField(null=True, blank=True)
    total_floors = models.IntegerField(null=True, blank=True)
    balconies = models.IntegerField(default=0)
    parking_type = models.CharField(max_length=20, choices=PARKING_CHOICES, null=True, blank=True)
    
    # 3. PG / Room Specific Fields
    SHARING_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', '2-Sharing'),
        ('TRIPLE', '3-Sharing'),
        ('QUADRUPLE', '4-Sharing'),
    )
    GENDER_CHOICES = (
        ('BOYS', 'Boys Only'),
        ('GIRLS', 'Girls Only'),
        ('COED', 'Co-ed / Everyone'),
    )
    
    sharing_type = models.CharField(max_length=20, choices=SHARING_CHOICES, null=True, blank=True)
    gender_preference = models.CharField(max_length=10, choices=GENDER_CHOICES, default='COED')
    is_for_students = models.BooleanField(default=True)
    is_for_professionals = models.BooleanField(default=True)
    
    # Amenities (Student/Bachelor Focused)
    ac_available = models.BooleanField(default=False)
    has_geyser = models.BooleanField(default=False)
    has_wardrobe = models.BooleanField(default=False)
    has_study_table = models.BooleanField(default=False)
    has_workspace_desk = models.BooleanField(default=False)
    has_ergonomic_chair = models.BooleanField(default=False)
    has_washing_machine = models.BooleanField(default=False)
    has_refrigerator = models.BooleanField(default=False)
    has_stove = models.BooleanField(default=False)
    has_microwave = models.BooleanField(default=False)
    has_coffee_maker = models.BooleanField(default=False)
    has_toaster = models.BooleanField(default=False)
    has_induction_plate = models.BooleanField(default=False)
    extra_amenities = models.TextField(blank=True, help_text="Additional amenities not mentioned above (comma separated)")
    
    food_provided = models.BooleanField(default=False)
    provides_breakfast = models.BooleanField(default=False)
    provides_lunch = models.BooleanField(default=False)
    provides_dinner = models.BooleanField(default=False)
    diet_type = models.CharField(max_length=20, choices=[('VEG', 'Pure Veg'), ('NONVEG', 'Non-Veg Allowed')], default='VEG')
    
    wifi_available = models.BooleanField(default=False)
    wifi_speed = models.IntegerField(default=0, help_text="Mbps")
    
    has_cctv = models.BooleanField(default=False)
    has_biometric = models.BooleanField(default=False)
    has_security_guard = models.BooleanField(default=False)
    
    # Safety Amenities
    has_smoke_alarm = models.BooleanField(default=False)
    has_carbon_monoxide_alarm = models.BooleanField(default=False)
    has_fire_extinguisher = models.BooleanField(default=False)
    has_first_aid_kit = models.BooleanField(default=False)
    has_emergency_exit_plan = models.BooleanField(default=False)
    
    laundry_service = models.BooleanField(default=False, help_text="Is laundry service provided?")
    
    # House Rules & Lifestyle
    VISITOR_POLICY_CHOICES = (
        ('ALLOWED', 'Visitors Allowed'),
        ('NO', 'No Visitors'),
        ('DAYTIME', 'Daytime Only'),
        ('OVERNIGHT', 'Overnight Allowed'),
    )
    visitor_policy = models.CharField(max_length=20, choices=VISITOR_POLICY_CHOICES, default='ALLOWED')
    curfew_time = models.CharField(max_length=50, default="No Curfew")
    smoking_allowed = models.BooleanField(default=False)
    alcohol_allowed = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    non_veg_allowed = models.BooleanField(default=True, help_text="Non-veg cooking allowed")
    extra_house_rules = models.TextField(blank=True, help_text="Additional rules or terms for tenants")
    
    # Location & Discovery
    nearby_landmarks = models.TextField(blank=True, help_text="e.g., 500m from College")
    connectivity_info = models.TextField(blank=True, help_text="Metro/BRTS distance")
    
    video_url = models.URLField(blank=True, help_text="Video tour link")
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
