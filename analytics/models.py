from django.db import models
from django.conf import settings
from property.models import Property

class PropertyView(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View of {self.property.title} at {self.viewed_at}"

class SearchActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='searches')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)
