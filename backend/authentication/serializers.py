from rest_framework import serializers
from .models import UserAccount
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
	confirm_password = serializers.CharField(write_only=True)  # For validation only
	avatar = serializers.ImageField(use_url=True, required=False)

	class Meta:
		model = UserAccount
		fields = ['id', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'avatar', 'user_state', 'nickname']
		extra_kwargs = {
			'password' : {'write_only' : True},
			'user_state' : {'read_only' : True}
		}

	def validate(self, data):
		print("hereee")
		if 'password' in data and (data['password'] != data['confirm_password']):
			raise serializers.ValidationError("Passwords do not match.")
		return data
	
	def create(self, validated_data):
		# Remove password2 as it's not part of the User model
		if 'confirm_password' in validated_data:
			validated_data.pop('confirm_password')
		# self.nickname = self.first_name + '_' + self.last_name
		# Hash the password before saving
		if 'password' in validated_data:
			validated_data['password'] = make_password(validated_data['password'])
		if 'first_name' in validated_data:
			validated_data['first_name'] = validated_data['first_name'].capitalize()
		if 'last_name' in validated_data:
			validated_data['last_name'] = validated_data['last_name'].capitalize()
		# Create and return the user
		return UserAccount.objects.create(**validated_data)

	# def	get_avatar_path(self, instance):
	# 	# print('instance.avatar: ', instance.avatar)
	# 	# print('instance.avatar.url: ', instance.avatar.url)
	# 	return instance.avatar.url[1:]


class UserAccountUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserAccount
		fields = ['first_name', 'last_name', 'avatar', 'nickname', 'email']
		extra_kwargs = {
			'first_name': {'required': True},
			'last_name': {'required': True},
			'avatar': {'required': True},
			'nickname': {'required': True},
			'email': {'required': True}
        				}

	def validate(self, data):

		if UserAccount.objects.filter(nick_name=data['nickname']).exclude(id=self.instance.id).exists():
			raise serializers.ValidationError("This nickname is already taken.")