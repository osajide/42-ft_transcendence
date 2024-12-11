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

	# def create(self, validated_data):
	#     # Pop the password from validated_data to handle it separately
	#     password = validated_data.pop('confirm_password')
		
	#     # Create the user instance without setting the password yet
	#     user = UserAccount(**validated_data)
	#     # user.save()  # Save the user with the hashed password
	#     return user


# from rest_framework import serializers
# from django.core.exceptions import ValidationError
# from django.contrib.auth import get_user_model

# User = get_user_model()
# class CreateUserSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(required=True)
#     email = serializers.EmailField(required=True)
#     password = serializers.CharField(write_only=True)
#     password2 = serializers.CharField(write_only=True, required=True)
#     class Meta:
#         model = User
#         fields = ("username", "email", "password", "password2")
#     def validate(self, attrs):
#         if attrs["password"] != attrs["password2"]:
#             raise serializers.ValidationError(
#                 {"password": "Password fields didn't match."}
#             )
#         return attrs
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             validated_data["username"], email=validated_data["email"], password=validated_data["password"]
#         )
#         user.is_active = False
#         user.save()
#         return user