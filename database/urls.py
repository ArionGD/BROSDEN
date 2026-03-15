from django.urls import path
from . import views

app_name = 'database'

urlpatterns = [
    path('schema/', views.database_schema, name='schema'),
]
