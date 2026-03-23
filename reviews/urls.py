from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/property/<int:booking_id>/', views.add_property_review, name='add_property_review'),
    path('add/tenant/<int:booking_id>/', views.add_tenant_review, name='add_tenant_review'),
    path('owner/list/', views.owner_reviews_list, name='owner_list'),
]
