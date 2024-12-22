from django.urls import path
from .consumers import *

websocket_url_patterns = [
	# re_path(r'chat/(?P<conversation_name>\d+_\d+)$', ChatConsumer.as_asgi()),
	path('ws/chats/<int:id>', ChatConsumer.as_asgi()),
	# re_path(r'chat/(?P<conversation_name>\w+)$', ChatConsumer.as_asgi()),
	# path('chat/<int:id>', ChatConsumer.as_asgi())
]