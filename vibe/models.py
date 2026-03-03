from django.db import models
from property.models import Property

class PropertyVibe(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='vibe')
    party_score = models.FloatField(default=0.0)
    study_score = models.FloatField(default=0.0)
    shopping_score = models.FloatField(default=0.0)
    residential_score = models.FloatField(default=0.0)
    
    # Store the dominant vibe
    top_vibe = models.CharField(max_length=50, blank=True, null=True)
    
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.property.title} Vibe - {self.top_vibe}"

    def get_max_vibe(self):
        scores = {
            'Party': self.party_score,
            'Study': self.study_score,
            'Shopping': self.shopping_score,
            'Residential': self.residential_score
        }
        max_vibe = max(scores, key=scores.get)
        # If all scores are 0, return Neutral
        if scores[max_vibe] == 0:
            return 'Neutral'
        return max_vibe
    
    def save(self, *args, **kwargs):
        self.top_vibe = self.get_max_vibe()
        super().save(*args, **kwargs)
