from django.urls import path
from . import views

app_name = 'contract'

urlpatterns = [
    path('view/<int:contract_id>/', views.view_contract, name='view'),
    path('receipt/deposit/<int:receipt_id>/', views.view_deposit_receipt, name='deposit_receipt'),
    path('receipt/contract/<int:contract_id>/', views.view_contract_receipt, name='contract_receipt'),
    path('sign/<int:contract_id>/', views.sign_contract, name='sign_contract'),
    path('rent-management/', views.rent_dashboard, name='rent_dashboard'),
    path('rent-management/mark-paid/<int:schedule_id>/', views.mark_rent_paid, name='mark_rent_paid'),
]
