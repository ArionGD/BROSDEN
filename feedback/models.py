from django.db import models
from contract.models import Contract
from property.models import Property
from django.conf import settings

class FeedbackRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Submission'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired/Ignored'),
    )

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='feedback_requests')
    due_date = models.DateField(help_text="The monthly anniversary date this feedback is due.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback Request for {self.contract.booking.property.title} due {self.due_date}"

class MonthlyFeedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    feedback_request = models.OneToOneField(FeedbackRequest, on_delete=models.CASCADE, related_name='submission')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='monthly_feedbacks')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_feedbacks')
    
    # Specific metrics for precise calculation
    maintenance_rating = models.IntegerField(choices=RATING_CHOICES, default=5, help_text="1 to 5 rating")
    responsiveness_rating = models.IntegerField(choices=RATING_CHOICES, default=5, help_text="1 to 5 rating")
    safety_rating = models.IntegerField(choices=RATING_CHOICES, default=5, help_text="1 to 5 rating")
    vibe_rating = models.IntegerField(choices=RATING_CHOICES, default=5, help_text="Neighborhood/Hostel vibe")
    
    comments = models.TextField(blank=True, help_text="Any issues or highlights this month?")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.property.title} by {self.tenant.username} on {self.submitted_at.date()}"

    def get_average_rating(self):
        return (self.maintenance_rating + self.responsiveness_rating + self.safety_rating + self.vibe_rating) / 4.0

