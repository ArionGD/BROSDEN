from django.urls import path
from . import views

app_name = 'map'

urlpatterns = [
    path('explore/', views.fullscreen_map, name='explore'),
    path('smart-api/', views.smart_recommend_api, name='smart_recommend_api'),
]
