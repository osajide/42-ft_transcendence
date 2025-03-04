from django.db import models
from authentication.models import UserAccount

# Create your models here.

class	Notification(models.Model):
	description = models.CharField(max_length=150)
	sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='sent_notifications')
	receiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='received_notifications')
	timestamp = models.DateTimeField(auto_now_add=True)
	# need to make choices for type
	type = models.CharField(max_length=100)

	class Meta:
		ordering = ['-timestamp']

	def	__str__(self):
		return f'{self.id} :{self.description}'