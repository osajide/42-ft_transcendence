from rest_framework import serializers
from .models import UserAccount
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
	confirm_password = serializers.CharField(write_only=True)  # For validation only
	avatar = serializers.SerializerMethodField(method_name='get_avatar_path')

	class Meta:
		model = UserAccount
		fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'id', 'avatar', 'user_state']
		extra_kwargs = {
			'password' : {'write_only' : True},
			# 'user_state' : {'read_only' : True}
		}

	def validate(self, data):
		if data['password'] != data['confirm_password']:
			print("here")
			raise serializers.ValidationError("Passwords do not match.")
		return data
	
	def create(self, validated_data):
		# Remove password2 as it's not part of the User model
		validated_data.pop('confirm_password')

		# Hash the password before saving
		validated_data['password'] = make_password(validated_data['password'])
		validated_data['first_name'] = validated_data['first_name'].capitalize()
		validated_data['last_name'] = validated_data['last_name'].capitalize()
		# Create and return the user
		return UserAccount.objects.create(**validated_data)

	def	get_avatar_path(self, instance):
		# print('instance.avatar: ', instance.avatar)
		# print('instance.avatar.url: ', instance.avatar.url)
		return instance.avatar.url[1:]

	