from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('submit/<int:request_id>/', views.submit_feedback, name='submit'),
]
