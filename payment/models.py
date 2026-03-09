from django.db import models
from django.conf import settings

class PaymentReceipt(models.Model):
    PAYMENT_TYPES = (
        ('SECURITY_DEPOSIT', 'Security Deposit'),
        ('RENT', 'Monthly Rent'),
        ('OTHER', 'Other Fee'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receipts')
    booking = models.ForeignKey('booking.BookingRequest', on_delete=models.SET_NULL, null=True, blank=True)
    property_title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    security_deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contract_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='SECURITY_DEPOSIT')
    period_month = models.IntegerField(null=True, blank=True)
    period_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.transaction_id} - {self.payment_type}"
