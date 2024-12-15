from rest_framework import serializers
from .models import Friendship
from authentication.serializers import UserSerializer

class	FriendshipSerializer(serializers.ModelSerializer):
	# sender = UserSerializer()
	# receiver = UserSerializer()
	class Meta:
		model = Friendship
		fields = ['sender', 'receiver', 'status']
