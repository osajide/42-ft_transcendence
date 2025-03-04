from rest_framework import serializers
from .models import *


class TournamentSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Tournament
		fields = ['id', 'start_date']
		extra_kwargs = {
			'start_date' : {'read_only' : True}
		}


class TournamentParticipantSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Tournament_Particapent
		fields = ['id', 'user_id', 'tournament_id']
		extra_kwargs = {
			'id' : {'read_only' : True}
		}
