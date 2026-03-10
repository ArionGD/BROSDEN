from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('kyc/tenant/', views.tenant_kyc_view, name='tenant_kyc'),
    path('kyc/owner/', views.owner_kyc_view, name='owner_kyc'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.account_settings_view, name='account_settings'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('premium/', views.pro_landing_view, name='premium_landing'),
    path('premium/upgrade/<str:tier>/', views.upgrade_tier_view, name='upgrade_tier'),
]
