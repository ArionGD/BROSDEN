from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TENANT', 'Tenant'),
        ('OWNER', 'Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='TENANT')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_tenant(self):
        return self.role == 'TENANT'

    @property
    def is_owner(self):
        return self.role == 'OWNER'
