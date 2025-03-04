from django.urls import path, re_path
from .consumers import GameConsumer

websocket_url_patterns = [
	path('ws/game/<int:id>', GameConsumer.as_asgi()),	
]
