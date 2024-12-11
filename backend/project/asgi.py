"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from authentication.middlewares import CookiesMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

asgi_application = get_asgi_application()

import chat.routing, notification.routing, game.routing, tournament.routing

application = ProtocolTypeRouter(
	{
		'http': asgi_application,
		'websocket': AllowedHostsOriginValidator(
			CookiesMiddleware(
				URLRouter(
					chat.routing.websocket_url_patterns
						+ notification.routing.websocket_url_patterns
							+ game.routing.websocket_url_patterns
							+ tournament.routing.websocket_url_patterns)
			)
		)
	}
)
