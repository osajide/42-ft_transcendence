from django.urls import path
from .consumers import NotificationConsumer

websocket_url_patterns = [
	path('ws/', NotificationConsumer.as_asgi())
]