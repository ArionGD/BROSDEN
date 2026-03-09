from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('<int:process_id>/', views.onboarding_dashboard, name='dashboard'),
    path('<int:process_id>/condition/upload/', views.upload_condition_report, name='upload_condition'),
    path('inventory/<int:item_id>/confirm/', views.confirm_inventory, name='confirm_inventory'),
    path('<int:process_id>/finalize/', views.mark_handover_complete, name='finalize'),
]
