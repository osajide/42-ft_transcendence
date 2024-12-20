from authentication.middlewares import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q, Max
from .models import Conversation
from .serializers import ConversationSerializer
from authentication.models import UserAccount
from authentication.serializers import UserSerializer
from friend.models import Friendship
from friend.views import get_friends
from django.http import JsonResponse

# Create your views here.

def serialize_result(users):
    users_list = []
    for user in users:
        serializer = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar': user.avatar.url[1:],
            'seen': user.seen,
            'email': user.email,
            'user_state': user.user_state
        }
        users_list.append(serializer)
    
    return users_list

@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_conversations(request):

    user = request.user

    conversations = Conversation.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).annotate(latest_message_timestamp=Max('messages__timestamp')).order_by('-latest_message_timestamp')

    print('conversations: ', conversations)

    if conversations is not None:
        print('len dyal conversations: ', len(conversations))
        users = []
        for conversation in conversations:
            last_message = conversation.messages.all().last()
            print('last message: ', last_message)
            if last_message is None:
                continue
            print('last content: ', last_message.content)
            # print('seen: ', last_message.seen_by_receiver)
            # print('ownert: ', last_message.owner.id)
            # print('usert: ', user.id)
            if conversation.user1 == user:
                if last_message.seen_by_receiver == True or (last_message.seen_by_receiver == False and last_message.owner.id is user.id):
                    print('seeeeeeeen*******')
                    conversation.user2.seen = True
                elif last_message.seen_by_receiver == False and last_message.owner.id is not user.id:
                    conversation.user2.seen = False
                users.append(conversation.user2)
            else:
                if last_message.seen_by_receiver == True or (last_message.seen_by_receiver == False and last_message.owner.id is user.id):
                    print('seeeeeeeen---------')
                    conversation.user1.seen = True
                elif last_message.seen_by_receiver == False and last_message.owner.id is not user.id:
                    conversation.user1.seen = False
                users.append(conversation.user1)

        ser = serialize_result(users)
        print('****ser:::: ', [ser])
        return JsonResponse([ser], safe=False)


@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friend_with_no_conversation(request):
    user = request.user
    conversations = Conversation.objects.filter(
        Q(user1=user) | Q(user2=user)
    )

    friends_with_conversation = []
    for conversation in conversations:
        msgs = conversation.messages.all()
        if msgs:
            if conversation.user1 == user:
                friends_with_conversation.append(conversation.user2)
            else:
                friends_with_conversation.append(conversation.user1)
    
    friends = get_friends(user, 'accepted')

    friends_without_conversation = []
    for friend in friends:
        if friend not in friends_with_conversation:
            friends_without_conversation.append(friend)
    print(friends_without_conversation)
    serializer = UserSerializer(friends_without_conversation, many=True)
    return Response([serializer.data], status=status.HTTP_200_OK)