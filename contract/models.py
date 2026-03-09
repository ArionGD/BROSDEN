from django.db import models
from django.conf import settings
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
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

    def generate_schedule(self):
        """Generates 12 months of rent records starting from the booking move-in date."""
        if self.rent_schedules.exists():
            return
        
        start_date = self.booking.move_in_date or date.today()
        # Ensure we are using a date object
        if hasattr(start_date, 'date'):
             start_date = start_date.date()

        for i in range(12):
            due_date = start_date + relativedelta(months=i)
            RentSchedule.objects.create(
                contract=self,
                due_date=due_date,
                amount=self.booking.property.price,
                status='UNPAID'
            )

    def __str__(self):
        return f"Contract for {self.booking.property.title} - {self.booking.tenant.username}"

class RentSchedule(models.Model):
    STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    )

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='rent_schedules')
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    paid_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"Rent for {self.contract.booking.property.title} - {self.due_date}"
