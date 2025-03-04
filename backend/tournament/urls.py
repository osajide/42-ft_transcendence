from django.urls import path, include
from .views import *

urlpatterns = [
	path('create_tournament/', CreateTournament.as_view()),
	path('tournament_list/', AvailableTournaments.as_view()),
	path('join_tournament/<int:id>', JoinTournament.as_view()),
	path('get_tournament_by_id/<int:id>', GetTournamentById.as_view()),
]
