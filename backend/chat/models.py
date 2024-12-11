from django.db import models
from authentication.models import UserAccount

# Create your models here.

class	Conversation(models.Model):
	user1 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='conversations_as_user1')
	user2 = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='conversations_as_user2')

	def	__str__(self):
		return f'{self.user1} and {self.user2}'
	
	def	save(self, *args, **kwargs):
		if self.user1.id < self.user2.id:
			self.name = f'{self.user1.id}_{self.user2.id}'
		else:
			self.name = f'{self.user2.id}_{self.user1.id}'
		return super().save(*args, **kwargs)
	
	class Meta:
		ordering = ['-id']

class	Message(models.Model):
	content = models.TextField(default="")
	timestamp = models.DateTimeField(auto_now_add=True)
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
	owner = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='messages')

	def	__str__(self):
		return f'{self.content}'
