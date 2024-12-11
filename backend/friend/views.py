from .models import Friendship
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from authentication.middlewares import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from authentication.models import UserAccount
from notification.models import Notification
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import UserSerializer
from django.db.models import Q, Case, When, Value, IntegerField
from .serializers import FriendshipSerializer
import re
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.

def	handle_friendship_deletion(friendship, action, user):
	if action == 'cancel':
		if friendship.last_action_by == user.id:
			friendship.delete()
		else:
			raise 403

	elif action == 'decline':
		if friendship.last_action_by != user.id:
			friendship.delete()
		else:
			raise 403

	else:
		if friendship.status != 'pending':
			friendship.delete()
		else:
			raise 403


	pass

def	notify_user(sender, receiver, action):
	sender = UserAccount.objects.get(id=sender)
	receiver = UserAccount.objects.get(id=receiver)
	description = ''
	notification_type = ''
	channel_layer = get_channel_layer()

	if action == 'invite':
		description = f'{sender.first_name} sends you an invitation'
		notification_type = 'invitation'
	else:
		description = f'You and {sender.first_name} are friends now!'
		notification_type = 'accept invitation'

	notification = Notification.objects.create(
		description=description, sender=sender, receiver=receiver, type=notification_type
	)
	async_to_sync(channel_layer.group_send)('notification',
									{
										'type': 'send_notification',
										'notification_type': notification_type, 
										'description': description,
										'receiver': receiver.id,
										'sender': sender,
										'timestamp': notification.timestamp
									}
	)


@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def	manage_friendship(request, action_target):
	action, id = action_target.split('_')

	user1 = request.user
	user2 = get_object_or_404(UserAccount, id=id)

	last_action_by = user1.id

	friendship = Friendship.objects.filter(
		Q(user1=user1.id, user2=user2.id) | Q(user1=user2.id, user2=user1.id)).first()
	try:
		if action == 'invite':
			if friendship == None and user1.id != user2.id:
				Friendship.objects.create(user1=request.user.id, user2=user2.id,
														last_action_by=last_action_by, status='pending')
				notify_user(request.user.id, user2.id, 'invite')
				return Response({'relationship': 'pending'}, status=status.HTTP_201_CREATED)
			raise 403

		relationship = ''

		if friendship == None:
			return Response(status=status.HTTP_404_NOT_FOUND)

		st = None
		if action == 'accept':
			if friendship.status == 'pending':
				friendship.status = relationship = 'accepted'
				friendship.last_action_by = last_action_by
				friendship.save()
				notify_user(request.user.id, user2.id, 'accept')
				st = 201
			else:
				raise 403

		elif action in ['decline', 'remove', 'cancel']:
			handle_friendship_deletion(friendship, action)
			st = 204

		elif action == 'block':
			if friendship.status == 'accepted':
				friendship.status = relationship = 'blocked'
				friendship.last_action_by = last_action_by
				friendship.save()
				st = 201
			else:
				raise 403

		elif action == 'unblock':
			if friendship.last_action_by == user1.id and friendship.status == 'block':
				friendship.status = relationship = 'accepted'
				friendship.status = relationship = 'accepted'
				friendship.last_action_by = last_action_by
				friendship.save()
				st = 201
			else:
				raise 403
		else:
			raise 405

	except int as e:
		return Response(status=e)

	return Response({'relationship': relationship}, status=st)


@api_view(['PATCH'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def	accept_friendship(request, friendship_name):
	list_id = friendship_name.split('_')
	id1 = int(list_id[0])
	id2 = int(list_id[1])

	if not request.user.id in [id1, id2]:
		return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

	friendship = get_object_or_404(Friendship, name=friendship_name)
	friendship.status = 'accepted'
	friendship.last_action_by = request.user.id
	
	return Response(status=status.HTTP_201_CREATED)


@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def	list_friends(request):
	id = request.user.id
	friends = Friendship.objects.filter((Q(user1=id) | Q(user2=id)) & Q(status='accepted') 
									).annotate(friend_id=Case(When(user1=id, then='user2'
									), default='user1', output_field=IntegerField()) 
									).values_list('friend_id', flat=True)

	users = UserAccount.objects.filter(id__in=friends)
	for user in users:
		print("friend : ", user)
	serializer = UserSerializer(users, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)

@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def	get_other_user_profile(request, id):

	user = get_object_or_404(UserAccount, id=id)
	try:
		friendship = Friendship.objects.get(Q(user1=request.user.id, user2=user.id)
									  			| Q(user1=user.id, user2=request.user.id))

		rel = friendship.status
		last_action_by = friendship.last_action_by
	except Friendship.DoesNotExist:
		rel = ''
		last_action_by = ''
	serializer = UserSerializer(user)
	return Response({
		'user': serializer.data,
		'rel': rel,
		'last_action_by': last_action_by
	}, status=status.HTTP_200_OK)

@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_matched_users(request, search_term):
	# remove spaces from first and last then remove duplicated spaces
	search_term = search_term.strip(' ')
	search_term = re.sub(r"\s+", " ", search_term)

	if ' ' in search_term :
		search_term = search_term.split(" ")
		print("first name : ", search_term[0])
		print("last name : ", search_term[1])
		users = UserAccount.objects.filter(first_name__iexact=search_term[0])
		users = users.filter(last_name__istartswith=search_term[1])
		print("Users : ", users)
	else:

		users = UserAccount.objects.annotate(
		match_priority=Case(
				When(first_name__istartswith=search_term, then=1),  
				When(last_name__istartswith=search_term, then=2),  
				output_field=IntegerField()
			)
		).filter(
			Q(first_name__istartswith=search_term) | Q(last_name__istartswith=search_term)
		).order_by('match_priority')  # Order by priority
		
	id = request.user.id
	friendships = Friendship.objects.filter((Q(user1=id) | Q(user2=id)) & Q(status='accepted') 
	).annotate(friend_id=Case(When(user1=id, then='user2'
	), default='user1', output_field=IntegerField()) 
	).values_list('friend_id', flat=True)
	excluded_ids = list(friendships)

	excluded_users = users.exclude(id__in=excluded_ids).exclude(id=request.user.id)
	serializer = UserSerializer(excluded_users, many=True)
		
	return Response(serializer.data, status=status.HTTP_200_OK)
