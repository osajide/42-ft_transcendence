from rest_framework import serializers
from .models import *
from authentication.serializers import UserSerializer

class	ConversationSerializer(serializers.ModelSerializer):
	user1 = UserSerializer()
	user2 = UserSerializer()
	class Meta:
		model = Conversation
		fields = '__all__'

class	MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = ['content', 'timestamp', 'owner']