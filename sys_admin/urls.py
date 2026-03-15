from django.urls import path
from . import views

app_name = 'sys_admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-matrix/', views.user_matrix, name='user_matrix'),
    path('operations/listing-requests/', views.listing_requests, name='listing_requests'),
    
    # KYC Operations
    path('operations/tenant-kyc/', views.tenant_kyc, name='tenant_kyc'),
    path('operations/tenant-kyc/<int:pk>/', views.tenant_kyc_detail, name='tenant_kyc_detail'),
    path('operations/owner-kyc/', views.owner_kyc, name='owner_kyc'),
    path('operations/owner-kyc/<int:pk>/', views.owner_kyc_detail, name='owner_kyc_detail'),
    
    # KYC Actions
    path('operations/kyc/<int:pk>/approve/', views.approve_kyc, name='approve_kyc'),
    path('operations/kyc/<int:pk>/reject/', views.reject_kyc, name='reject_kyc'),
    # Property Actions
    path('operations/property/<int:pk>/approve/', views.approve_property, name='approve_property'),
    path('operations/property/<int:pk>/reject/', views.reject_property, name='reject_property'),
    
    path('export-accounts-excel/', views.export_accounts_excel, name='export_accounts_excel'),
]
