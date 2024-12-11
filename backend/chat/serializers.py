from rest_framework import serializers
from .models import *

class	ConversationSerializer(serializers.ModelSerializer):
	participants = serializers.StringRelatedField(many=True)

	class Meta:
		model = Conversation
		fields = '__all__'

class	MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = ['content', 'timestamp', 'owner']