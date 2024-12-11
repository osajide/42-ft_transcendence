# from django.http import HttpResponse
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from .models import *
# from .serializers import *
# from rest_framework.views import APIView
# from rest_framework.decorators import api_view
# from django.shortcuts import get_object_or_404

# # Create your views here.

# # class	UserViewSet(viewsets.ModelViewSet):
# # 	queryset = User.objects.all()
# # 	serializer_class = UserSerializer

# # class	ConversationViewSet(viewsets.ModelViewSet):
# # 	queryset = Conversation.objects.get()
# # 	serializer_class = ConversationSerializer

# # class	MessageViewSet(viewsets.ModelViewSet):
# # 	queryset = Message.objects.all()
# # 	serializer_class = MessageSerializer

# # @login_required(login_url='/salam/')
# # def	salamView(request):
# # 	return HttpResponse("salam")

# # def test(request):
# # 	return HttpResponse('redirection')
	

# def	creating_testing_users_and_conversations(request):
# 	users_data = [
# 		{'first_name': 'Oussama', 'last_name': 'Sajide', 'username': 'osajide', 'email': 'osajide@gmail.com'},
# 		{'first_name': 'Mohemmed', 'last_name': 'Taib', 'username': 'mtaib', 'email': 'mtaib@gmail.com'},
# 		{'first_name': 'Yassine', 'last_name': 'Khayri', 'username': 'ykhayri', 'email': 'ykhayri@gmail.com'},
# 		{'first_name': 'Aymane', 'last_name': 'Bouabra', 'username': 'abouabra', 'email': 'abouabra@gmail.com'},
# 		{'first_name': 'Bader', 'last_name': 'Elkdioui', 'username': 'bel-kdio', 'email': 'bel-kdio@gmail.com'},
# 		{'first_name': 'Mohammed', 'last_name': 'Baanni', 'username': 'mbaanni', 'email': 'mbaanni@gmail.com'},
# 		{'first_name': 'Ali', 'last_name': 'Elamine', 'username': 'ael-amin', 'email': 'ael-amin@gmail.com'},
# 		{'first_name': 'Youssef', 'last_name': 'Khalil', 'username': 'ykhalil-', 'email': 'ykhali-@gmail.com'}
# 	]
# 	for user_data in users_data:
# 		User.objects.get_or_create(**user_data)
# 	return HttpResponse("CREATED", status=status.HTTP_201_CREATED)

# @api_view()
# def	get_conversations(request, id):
# 	user = get_object_or_404(User, id=id)
# 	conversations = Conversation.objects.filter(participants=user)
# 	serializer = ConversationSerializer(conversations, many=True)
# 	return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def	create_conversation(request):
# 	print('request.data: ', request.data)
# 	serializer = ConversationSerializer(data=request.data)
# 	if serializer.is_valid():
# 		print('data validated by the serializer')
# 		serializer.save()
# 		return Response(serializer.data, status=status.HTTP_201_CREATED)
# 	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def	get_friends_with_no_conversation(request, id):
# 	user = get_object_or_404(User, id=id)
# 	conversations = Conversation.objects.filter(participants=user)
# 	friends = user.friends
# 	friends_with_no_conversation = []

# 	found = None
# 	for friend in friends:
# 		for conversation in conversations:
# 			if friend in conversation.participants:
# 				found = 1
# 		if found == None:
# 			friends_with_no_conversation.append(friend)
# 			found == None
	
# 	Response(friends_with_no_conversation, status=status.HTTP_200_OK)
