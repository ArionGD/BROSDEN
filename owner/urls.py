from django.urls import path
from . import views

app_name = 'owner'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rent-received/', views.rent_received, name='rent_received'),
]
