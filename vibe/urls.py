from django.urls import path
from . import views

app_name = 'vibe'

urlpatterns = [
    path('check/<int:property_id>/', views.calculate_vibe, name='calculate_vibe'),
]
