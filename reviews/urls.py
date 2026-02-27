from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:property_id>/', views.add_review, name='add_review'),
    path('owner/list/', views.owner_reviews_list, name='owner_list'),
]
