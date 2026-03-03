from django.db import models
from django.conf import settings
from booking.models import BookingRequest

class OnboardingProcess(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    booking = models.OneToOneField(BookingRequest, on_delete=models.CASCADE, related_name='onboarding')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Progress Tracking
    inspection_complete = models.BooleanField(default=False)
    inventory_confirmed = models.BooleanField(default=False)
    utilities_transferred = models.BooleanField(default=False)
    orientation_done = models.BooleanField(default=False)
    keys_handed_over = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Onboarding for {self.booking.property.title} - {self.booking.tenant.username}"

    @property
    def progress_percentage(self):
        steps = [self.inspection_complete, self.inventory_confirmed, self.utilities_transferred, self.orientation_done, self.keys_handed_over]
        completed = sum(1 for step in steps if step)
        return (completed / len(steps)) * 100

class ConditionReport(models.Model):
    onboarding = models.ForeignKey(OnboardingProcess, on_delete=models.CASCADE, related_name='condition_reports')
    item_name = models.CharField(max_length=100, help_text="e.g., Living Room Walls, Kitchen Sink")
    description = models.TextField()
    image = models.ImageField(upload_to='onboarding/conditions/', null=True, blank=True)
    owner_verified = models.BooleanField(default=True)
    tenant_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Condition: {self.item_name} for {self.onboarding.booking.property.title}"

class RoomInventory(models.Model):
    """Specific for furnished properties, PGs, and Hostels."""
    onboarding = models.ForeignKey(OnboardingProcess, on_delete=models.CASCADE, related_name='inventory_items')
    item_name = models.CharField(max_length=100, help_text="e.g., Study Table, Mattress, Locker Key")
    condition = models.CharField(max_length=50, default='GOOD')
    is_confirmed_by_tenant = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Inventory: {self.item_name} ({self.condition})"

class UtilityOrService(models.Model):
    SERVICE_TYPES = (
        ('POWER', 'Electricity/Power'),
        ('WATER', 'Water Supply'),
        ('GAS', 'Gas Connection'),
        ('INTERNET', 'Internet/WiFi'),
        ('MESS', 'Mess/Meal Timings'),
    )
    
    onboarding = models.ForeignKey(OnboardingProcess, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    details = models.TextField(help_text="Instructions, timings, or account details")
    is_transferred_or_ready = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_service_type_display()} for {self.onboarding.booking.tenant.username}"

class OrientationGuide(models.Model):
    onboarding = models.OneToOneField(OnboardingProcess, on_delete=models.CASCADE, related_name='guide')
    rules_and_regulations = models.TextField(help_text="Curfew, guest policies, noise rules")
    meal_menu = models.TextField(blank=True, help_text="Weekly menu for PGs/Hostels")
    caretaker_contact = models.CharField(max_length=255, blank=True)
    is_read_by_tenant = models.BooleanField(default=False)

    def __str__(self):
        return f"Orientation for {self.onboarding.booking.property.title}"
