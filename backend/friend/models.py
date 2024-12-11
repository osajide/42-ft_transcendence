from django.db import models

# Create your models here.

class	Friendship(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('blocked', 'Blocked'),
	]

	user1 = models.BigIntegerField()		# Represents the first user
	user2 = models.BigIntegerField()		# Represents the second user
	status = models.CharField(
		max_length=10,
		choices=STATUS_CHOICES,
		default='pending'
	)
	last_action_by = models.BigIntegerField()

	def	__str__(self):
		return f'{self.user1} and {self.user2}, last action made by: {self.last_action_by}'
