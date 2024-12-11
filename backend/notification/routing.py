from django.urls import path
from .consumers import NotificationConsumer

websocket_url_patterns = [
	path('', NotificationConsumer.as_asgi())
]