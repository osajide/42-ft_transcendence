from django.urls import re_path, path
from .views import *

urlpatterns = [
	re_path(r'(?P<action_target>[a-z]+_\d+)$', manage_friendship),
	# path('accept/<str:friendship_name>/', accept_friendship),
	path('list/', list_friends),
	path('profile/<int:id>/', get_other_user_profile),
	path('search/<str:search_term>/', get_matched_users)
]