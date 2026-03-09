from django.urls import path
from django.urls import path
from . import views

app_name = 'property'

urlpatterns = [
    path('browse/', views.browse_properties, name='browse'),
    path('my-properties/', views.owner_property_list, name='owner_list'),
    path('add/', views.add_property, name='add_property'),
    path('edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('image/delete/<int:pk>/', views.delete_property_image, name='delete_image'),
    path('<int:pk>/', views.property_detail, name='detail'),
]
