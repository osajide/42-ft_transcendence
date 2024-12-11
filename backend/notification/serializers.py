from rest_framework import serializers
from .models import Notification
from authentication.serializers import UserSerializer

class	NotificationSerializer(serializers.ModelSerializer):
	sender = UserSerializer()
	class Meta:
		model = Notification
		fields = ['id', 'description', 'type', 'sender', 'timestamp']