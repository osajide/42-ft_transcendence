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
from authentication.views import UserProfile
# from .serializers import FriendshipSerializer
import re
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.

def	handle_friendship_deletion(friendship, action, user):
	if action == 'cancel':
		if friendship.last_action_by == user.id:
			friendship.delete()
		else:
			return 403

	elif action == 'decline':
		if friendship.last_action_by != user.id:
			friendship.delete()
		else:
			return 403

	else:
		if friendship.status != 'pending':
			friendship.delete()
		else:
			return 403
		
	return 201

def	notify_user(sender, receiver, action):
	description = ''
	notification_type = ''
	channel_layer = get_channel_layer()

	if action == 'invite':
		description = f'{sender.first_name} have sent you an invitation'
		notification_type = 'invitation'
	else:
		description = f'You and {sender.first_name} are friends now!'
		notification_type = 'accept'

	print('receiver: ', receiver)
	notification = Notification.objects.create(
		description=description, sender=sender, receiver=receiver, type=notification_type
	)
	print('notification: ', notification)
	async_to_sync(channel_layer.group_send)('notification',
									{
										'type': 'send_notification',
										'notification_type': notification_type, 
										'description': description,
										'receiver': UserSerializer(receiver).data,
										'sender': UserSerializer(sender).data,
										'timestamp': str(notification.timestamp)
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
		Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)).first()
	
	if action == 'invite':
		if friendship == None and user1.id != user2.id:
			Friendship.objects.create(user1=request.user, user2=user2,
													last_action_by=last_action_by, status='pending')
			notify_user(user1, user2, 'invite')
			return Response({'relationship': 'pending'}, status=status.HTTP_201_CREATED)
		return Response({'error': 'Friendship already exists'}, status=status.HTTP_200_OK)

	relationship = ''

	if friendship == None:
		return Response(status=status.HTTP_404_NOT_FOUND)

	st = 201
	if action == 'accept':
		if friendship.status == 'pending':
			friendship.status = relationship = 'accepted'
			friendship.last_action_by = last_action_by
			friendship.save()
			notify_user(user1, user2, 'accept')
		else:
			return Response({'error': 'The invitation was canceled'}, status=status.HTTP_200_OK)

	elif action in ['decline', 'remove', 'cancel']:
		ret = handle_friendship_deletion(friendship, action, user1)
		if ret == 403:
			return Response({'error': 'Something went wrong'}, status=status.HTTP_200_OK)
		st = ret

	elif action == 'block':
		if friendship.status == 'accepted':
			friendship.status = relationship = 'blocked'
			friendship.last_action_by = last_action_by
			friendship.save()
			
		else:
			return Response({"error": "Something went wrong"}, status=status.HTTP_200_OK)

	elif action == 'unblock':
		if friendship.last_action_by == user1.id and friendship.status == 'blocked':
			friendship.status = relationship = 'accepted' 
			friendship.last_action_by = last_action_by
			friendship.save()
		else:
			return Response({'error': 'Something went wrong'}, status=status.HTTP_200_OK)
	else:
		return Response({'error': 'Something went wrong'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
	# print('heere: ', {'relationship': relationship})
	return Response({'relationship': relationship}, status=st)


# @api_view(['PATCH'])
# @authentication_classes([CookieJWTAuthentication])
# @permission_classes([IsAuthenticated])
# def	accept_friendship(request, friendship_name):
# 	list_id = friendship_name.split('_')
# 	id1 = int(list_id[0])
# 	id2 = int(list_id[1])

# 	if not request.user.id in [id1, id2]:
# 		return Response({'error': 'Access denied'}, status=status.HTTP_200_OK)

# 	friendship = get_object_or_404(Friendship, name=friendship_name)
# 	friendship.status = 'accepted'
# 	friendship.last_action_by = request.user.id
	
# 	return Response(status=status.HTTP_201_CREATED)


def	get_friends(user, status):
	if status == 'pending':
		friendships = Friendship.objects.filter(
			(Q(user1=user) | Q(user2=user)) & Q(status=status) & ~Q(last_action_by=user.id))
	elif status == 'new friend':
		friendships = Friendship.objects.filter(
			(Q(user1=user) | Q(user2=user))
				& ((Q(status='pending') & ~Q(last_action_by=user.id))
	   				| (Q(status='blocked') & ~Q(last_action_by=user.id)) | Q(status='accepted')))
	else:
		friendships = Friendship.objects.filter(
			(Q(user1=user) | Q(user2=user)) & Q(status=status))
	
	friends = []

	for friendship in friendships:
		if friendship.user1 == user:
			friends.append(friendship.user2)
		else:
			friends.append(friendship.user1)
	
	return sorted(friends, key=lambda friend: (friend.first_name, friend.last_name))

@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def	list_friends(request):

	user = request.user
	friends = get_friends(user, 'accepted')
	invitations = get_friends(user, 'pending')
	serializer = UserSerializer(invitations, many=True)
	serializer1 = UserSerializer(friends, many=True)

	return Response([serializer.data, serializer1.data], status=status.HTTP_200_OK)

@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def	get_other_user_profile(request, id):
    request.profile =  UserAccount.objects.get(id=id)
    view = UserProfile()
    response = view.get(request=request)
    return response

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
	
	friends = get_friends(request.user, 'new friend')

	excluded_ids = []
	for friend in friends:
		excluded_ids.append(friend.id)

	excluded_users = users.exclude(
		Q(id__in=excluded_ids) | Q(id=request.user.id))

	serializer = UserSerializer(excluded_users, many=True)

	return Response([serializer.data], status=status.HTTP_200_OK)

