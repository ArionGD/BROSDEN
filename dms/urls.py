from django.urls import path
from . import views

app_name = 'dms'

urlpatterns = [
    # Admin Views
    path('admin/vault/', views.admin_document_vault, name='admin_vault'),
    path('admin/document/<int:pk>/approve/', views.approve_document, name='approve_document'),
    
    # User Views
    path('my-documents/', views.my_documents, name='my_documents'),
]
