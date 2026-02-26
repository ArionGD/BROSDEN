from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('kyc/', views.kyc_form_view, name='kyc_form'),
    path('checkout/', views.razorpay_checkout, name='checkout'),
    path('success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('receipt/<int:receipt_id>/', views.view_receipt, name='view_receipt'),
]
