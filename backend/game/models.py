from django.db import models
from authentication.models import UserAccount

# Create your models here.

class	Game(models.Model):
	player1 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="games_as_player1")
	player2 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="games_as_player2")
	
	player1_score = models.IntegerField(default=0)
	player2_score = models.IntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	
	TYPES = [
		('solo', 'Solo'),
		('tournament', 'Tournament'),
	]

	game_type = models.CharField(max_length=10, choices=TYPES)
	winner = models.IntegerField(default=0)

	def	__str__(self):
		return f'{self.player1.id}:{self.player1.first_name} vs {self.player2.id}:{self.player2.first_name}: winner id {self.winner}'
