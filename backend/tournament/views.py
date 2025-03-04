from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework import status
from authentication.middlewares import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class CreateTournament(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = TournamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableTournaments(APIView):
    # authentication_classes = [CookieJWTAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self,request):
		
        available_tournaments = Tournament.objects.exclude(participants__id=request.user.id, status="finished")
        serializer = TournamentSerializer(available_tournaments, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class JoinTournament(APIView):

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request, id):

        if not Tournament_Particapent.objects.filter(tournament_id=id).exists():
            return Response({'error': 'Tournamnet not found'}, status=status.HTTP_400_BAD_REQUEST)

        tournaments = Tournament_Particapent.objects.filter(tournament_id=id, user_id=request.user.id)

        if tournaments.exists():
            return Response({'error': 'Player is already joined the tournament'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Tournament_Particapent.objects.filter(user_id=request.user.id).exists():
            return Response({'error': 'Player is already joined a tournament'}, status=status.HTTP_400_BAD_REQUEST)

        if Tournament_Particapent.objects.filter(tournament_id=id).count() >= 8:
            return Response({'error': 'Tournamnet is Full'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Tournament_Particapent.objects.filter(tournament_id=id, status="finished").exists():
            return Response({'error': 'The required Tournament is over'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TournamentParticipantSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTournamentById(APIView):

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request, id):
		
        try:
            tournament = Tournament.objects.get(id=id)
            serializer = TournamentSerializer(tournament)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Tournament.DoesNotExist:
            return Response({'error' : 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)


# get tournaments for a specific user 

class PlayedTournaments(APIView):

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):

        tournaments = Tournament_Particapent.objects.get(user_id=request.user.id)

        serializer = TournamentParticipantSerializer(tournaments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
