from django.db import models
from authentication.models import UserAccount

# Create your models here.

class	Friendship(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('blocked', 'Blocked'),
	]

	user1 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='friendship_as_user1')
	user2 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='friendship_as_user2')

	status = models.CharField(
		max_length=10,
		choices=STATUS_CHOICES,
		default='pending'
	)

	last_action_by = models.BigIntegerField()

	def	__str__(self):
		return f'{self.user1} and {self.user2}, last action made by: {self.last_action_by}'
	
	# class Meta:
	# 	ordering = ['']
