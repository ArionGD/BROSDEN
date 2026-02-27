from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('tenant/kyc/', views.tenant_kyc_view, name='tenant_kyc'),
    path('owner/kyc/', views.owner_kyc_view, name='owner_kyc'),
    path('checkout/', views.razorpay_checkout, name='checkout'),
    path('success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('receipt/<int:receipt_id>/', views.view_receipt, name='view_receipt'),
    path('history/', views.payment_history, name='history'),
]
