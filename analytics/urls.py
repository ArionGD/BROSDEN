from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('owner-insights/', views.owner_analytics, name='owner_dashboard'),
    path('tenant-insights/', views.tenant_analytics, name='tenant_dashboard'),
]
