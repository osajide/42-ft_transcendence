from django.urls import path
from . import views

urlpatterns = [
    path('chats/list/', views.get_conversations),
    path('chats/new/', views.get_friend_with_no_conversation),
]