from django.db import models
from authentication.models import UserAccount

# Create your models here.

class Tournament(models.Model):

    # name = models.CharField(max_length=20, unique=True)
    start_date = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(UserAccount, related_name="particapents", through='Tournament_Particapent')
    size = models.IntegerField(default=8)
    status_choices = [
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='active')
    winner = models.IntegerField(default=0)



class Tournament_Particapent(models.Model):

    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    tournament_id = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    class Meta:
        db_table = "tournament_tournament_particapents"

    def __str__(self) -> str:
        return f"{self.user_id}:{self.tournament_id}"
