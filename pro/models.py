from django.db import models
from django.conf import settings

class ProMembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pro_membership')
    tier = models.CharField(max_length=50, choices=[('BASIC', 'Basic Pro'), ('PLATINUM', 'Platinum Pro')], default='BASIC')
    is_active = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.tier} ({'Active' if self.is_active else 'Inactive'})"

class ProFeature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name
