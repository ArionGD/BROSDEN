from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('kyc/', views.kyc_form_view, name='kyc_form'),
    path('checkout/', views.razorpay_checkout, name='checkout'),
]
