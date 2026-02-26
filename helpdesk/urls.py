from django.urls import path
from . import views

app_name = 'helpdesk'

urlpatterns = [
    path('', views.support_home, name='home'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/new/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
]
