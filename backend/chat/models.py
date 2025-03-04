from django.db import models
from authentication.models import UserAccount

# Create your models here.

class	Conversation(models.Model):
	user1 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='conversations_as_user1')
	user2 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='conversations_as_user2')

	def	__str__(self):
		return f'{self.user1} and {self.user2}'
	
	# class Meta:
	# 	ordering = ['messages__timestamp']

class	Message(models.Model):
	content = models.TextField(default="")
	timestamp = models.DateTimeField(auto_now_add=True)
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
	owner = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='messages')
	seen_by_receiver = models.BooleanField(default=False)

	def	__str__(self):
		return f'{self.content}'
	
	class Meta:
		ordering = ['timestamp']
