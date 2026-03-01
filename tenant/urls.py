from django.urls import path
from . import views

app_name = 'tenant'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rent-payments/', views.rent_payments, name='rent_payments'),
]
