from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('homev2/', views.index_v2, name='index_v2'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
