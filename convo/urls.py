from django.urls import path
from . import views

app_name = 'convo'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:conversation_id>/', views.chat_box, name='chat_box'),
    path('start/<int:user_id>/', views.start_conversation, name='start'),
]
