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

# Create your views here.

@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_conversations(request):

    data = []
    user = request.user

    conversations = Conversation.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).annotate(latest_message_timestamp=Max('messages__timestamp')).order_by('-latest_message_timestamp')

    print('conversations: ', conversations)

    if conversations is not None:
        users = []
        for conversation in conversations:
            if conversation.user1 == user:
                users.append(conversation.user2)
            else:
                users.append(conversation.user1)
        serializer = UserSerializer(users, many=True)
        data = [serializer.data]
    
    print('data::: ', data.__len__())
    return Response(data, status=status.HTTP_200_OK)


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