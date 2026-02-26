from django.urls import path
from . import views

app_name = 'contract'

urlpatterns = [
    path('view/<int:contract_id>/', views.view_contract, name='view'),
]
