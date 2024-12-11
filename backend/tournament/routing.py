from django.urls import path
from . import consumers
from .consumers import *

websocket_url_patterns = [

    # path('', consumers.TournamentConsumer.as_asgi()),
    path('tournament/<int:tournament_id>', TournamentConsumer.as_asgi()),
]
