from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('checkout/', views.razorpay_checkout, name='checkout'),
    path('success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('receipt/<int:receipt_id>/', views.view_receipt, name='view_receipt'),
    path('receipt/<int:receipt_id>/download/', views.download_receipt_pdf, name='download_receipt_pdf'),
    path('history/', views.payment_history, name='history'),
]
