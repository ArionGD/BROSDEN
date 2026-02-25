from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('request/<int:property_id>/', views.create_booking, name='create'),
    path('my-requests/', views.tenant_booking_list, name='tenant_bookings'),
    path('requests/', views.owner_booking_list, name='owner_bookings'),
    path('handle/<int:booking_id>/<str:action>/', views.handle_booking, name='handle'),
]
