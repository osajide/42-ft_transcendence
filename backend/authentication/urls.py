from django.contrib import admin
from django.urls import path, include
from .views import *
from .oauth import GetAuthCode, OAuthCallback

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name= 'register'),
    path('activate/<str:token>/', ActivateUserAPIView.as_view(), name='activate_user'),
    path('login/', LoginView.as_view(), name = 'login'),
    # path('user/', UserView.as_view(), name = 'user'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('refresh/', RefreshView.as_view(), name = 'refresh'),
    path('intra/redirect/', GetAuthCode.as_view(), name='auth-code'),
    path('intra/oauth/', OAuthCallback.as_view(), name='oauth_callback'),
    path('add_multiple_users/', AddMultipleUsersView.as_view(), name='add_users'),
    path('profile/', UserProfile.as_view(), name='profile')
]