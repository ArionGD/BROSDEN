from django.urls import path
from . import views

app_name = 'pro'

urlpatterns = [
    path('membership/', views.pro_landing, name='landing'),
    path('upgrade/<str:tier>/', views.upgrade_tier, name='upgrade'),
]
