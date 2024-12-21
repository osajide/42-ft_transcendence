from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .tokens import get_tokens_for_user
from .tokens import send_email
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .tokens import token_decoder
from .models import UserAccount
from game.models import Game
from tournament.models import *
from django.db.models import Q, F, Sum, Case, When, Value, IntegerField, CharField
import jwt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .middlewares import CookieJWTAuthentication
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework.decorators import authentication_classes, permission_classes
from .decorators import two_fa_required
from django.utils.decorators import method_decorator
from .two_fa import *
from friend.models import Friendship
import json

# Create your views here.

# class RegisterUserAPIView(APIView):
#     def post(self, request):

#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             # send_email(user, request)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer

class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # send_email(user, request)  # Uncomment this when ready
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Log the errors before returning the response
        print("Validation Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateUserAPIView(APIView):
    def get(self, request, token):
        
        # Decode the token to get the user id

        user_id = token_decoder(token)

        if (user_id == -1):
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            user_id = decoded_data.get('user_id')
            send_email(UserAccount.objects.get(id=user_id), request)
            return Response({'message': 'Resent verification email'}, status=status.HTTP_200_OK)

        #     send_email(UserAccount.objects.filter, request)
        try:
            user = get_object_or_404(UserAccount, pk=user_id)
            if (user.verified_mail == True):
                return Response({'message': 'Account already activated'}, status=status.HTTP_200_OK)

            user.verified_mail = True
            user.save() 
            
            return Response({'message': 'Account activated successfully!'}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'error': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)
    

# class LoginView(APIView):
    # def post(self, request):
    
    #     try : 
    #         email = request.data['email']
    #         password = request.data['password']
    #     except KeyError as e:
    #         return Response({'error':'Not provided enough data'})
       
        
    #     user = UserAccount.objects.filter(email = email).first()
        
    #     if user is None:
    #         raise Response({'error':'User not found'})
        
    #     if not check_password(password, user.password):
    #         return Response({'error':'Incorrect password'})
        
    #     if (user.verified_mail == False):
    #         return Response({'error': 'You have to activate your account'})
    #     token = get_tokens_for_user(user)
        
    #     # response = Response({
    #     #     "acess_token" : token['access']
    #     # })
    #     serializer = UserSerializer(user)
    #     response =  Response({
    #         'message': 'successfully Logged',
    #         'user': serializer.data
    #         } , status=status.HTTP_200_OK)

    #     print("refresh token", token['refresh'])
    #     print("access token", token['access'])


    #     response.set_cookie(key = 'refresh_token', value=token['refresh'], httponly=True)
    #     response.set_cookie(key = 'access_token', value=token['access'], httponly=True)
    #     return response

class LoginView(APIView):
    def post(self, request):
    
        try : 
            email = request.data['email']
            password = request.data['password']
        except KeyError as e:
            return Response({'error':'Not provided enough data'})
       
        
        user = UserAccount.objects.filter(email = email).first()
        
        if user is None:
            return Response({'error':'User not found'})
        
        if not check_password(password, user.password):
            return Response({'error':'Incorrect password'})
        
        if (user.verified_mail == False):
            return Response({'error': 'You have to activate your account'})
        token = get_tokens_for_user(user)
        
        # response = Response({
        #     "acess_token" : token['access']
        # })
        # serializer = UserSerializer(user)
        # response =  Response({
        #     'message': 'successfully Logged',
        #     'user': serializer.data
        #     } , status=status.HTTP_200_OK)

        print("refresh token", token['refresh'])
        print("access token", token['access'])

        if user.is_2fa_verified == True:
            response =  Response({'verify_otp'})
        else:
            response =  Response({'scan_qr'})
            
        response.set_cookie(key = 'refresh_token', value=token['refresh'], httponly=True)
        response.set_cookie(key = 'access_token', value=token['access'], httponly=True)
        
        return response

class AddMultipleUsersView(APIView):
    def get(self, request, *args, **kwargs):
        user_data_list = [
        {'first_name': 'Oussama', 'last_name': 'Sajide', 'email': 'osajide@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Mohamed', 'last_name': 'Taib', 'email': 'mtaib@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Yassine', 'last_name': 'Khayri', 'email': 'ykhayri@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Aymane', 'last_name': 'Bouabra', 'email': 'abouabra@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Bader', 'last_name': 'Elkdioui', 'email': 'bel-kdio@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Mohammed', 'last_name': 'Baanni', 'email': 'mbaanni@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Ali', 'last_name': 'Elamine', 'email': 'ael-amin@gmail.com', "password": "1", "confirm_password": "1"},
		{'first_name': 'Youssef', 'last_name': 'Khalil', 'email': 'ykhali-@gmail.com', "password": "1", "confirm_password": "1"}
        ]

        created_users = []
        errors = []

        # Iterate through the user data and create users
        for user_data in user_data_list:
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                created_users.append(serializer.data)
            else:
                errors.append({"user_data": user_data, "errors": serializer.errors})

        # Return response based on the outcome
        if errors:
            return Response({"created_users": created_users, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

        return Response({"created_users": created_users}, status=status.HTTP_201_CREATED)
        
@method_decorator(two_fa_required, name='dispatch')
class LogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Corrected typo: access_token instead of acess_token

        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')  # Assuming refresh_token is the name

        print("==========USER LOGGED OUT")
        # Log out: print tokens to see the values (optional)
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)

        # Prepare the response and delete the cookies
        response = Response({'message': 'Logged out successfully'}, status=200)
        
        # Delete the access and refresh token cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        token = RefreshToken(refresh_token)
        token.blacklist()
       
        
        return response
    
class RefreshView(APIView):
    
    def post(self, request):

        ref_token = request.COOKIES.get('refresh_token')
        print('test')
        if ref_token is None:
            return Response({'error': 'Authentication credentials needed.'}, status=status.HTTP_403_FORBIDDEN)

        try:

            payload = jwt.decode(ref_token, settings.SECRET_KEY, algorithms=['HS256'])

            get_object_or_404(UserAccount, pk__in=payload['user_id'])

            refresh = RefreshToken(ref_token)

            response = Response({'message': 'generate new access token.'}, status=status.HTTP_200_OK)

            response.set_cookie(key='refresh_token', value=ref_token, httponly=True, samesite='None', secure=True)
            response.set_cookie(key='access_token', value=str(refresh.access_token), httponly=True, samesite='None', secure=True)
            return response
        except jwt.ExpiredSignatureError:
            print('ok')
            return Response({'error': 'Refresh token expired'}, status=status.HTTP_403_FORBIDDEN)
        except Http404:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator(two_fa_required, name='dispatch')
class UserProfile(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if hasattr(request, 'profile'):
            user = request.profile
        else:
            user = UserAccount.objects.filter(email=request.user.email).first()

        total_solo_games = Game.objects.filter(game_type='solo').filter(
                                            Q(player1=user) | Q(player2=user)).count()
        
        total_played_tournament = Tournament_Particapent.objects.filter(user_id=user.id).count()
        
        print("id : ", user.id)
        total_win_games = Game.objects.filter(game_type='solo', winner=user.id).filter(
                                            Q(player1=user) | Q(player2=user)).count()


        total_win_tournaments = Tournament.objects.filter(winner=user.id).count()


        total_loss_games = Game.objects.filter(game_type='solo').filter(
                        Q(player1=user) | Q(player2=user)).exclude(winner=user.id).count()


        played_tournaments = Tournament_Particapent.objects.filter(user_id=user.id).values('tournament_id')
        total_loss_tournaments = Tournament.objects.filter(id__in=played_tournaments).exclude(winner=user.id).count()
        
        # recent_games = (
        #                 Game.objects.filter(
        #                     Q(player1=user) | Q(player2=user)
        #                 )
        #                 .annotate(
        #                     user_score=Case(
        #                         When(player1=user, then=F("player1_score")),
        #                         When(player2=user, then=F("player2_score")),
        #                         default=Value(0),
        #                         output_field=IntegerField(),
        #                     ),
        #                     result=Case(
        #                         When(winner=user.id, then=Value("Win")),
        #                         default=Value("Loss"),
        #                         output_field=CharField(),
        #                     ),
        #                     opponent_avatar=Case(
        #                         When(player1=user, then=F("player1_avatar")),
        #                         When(player2=user, then=F("player2_avatar")),
        #                         default='user.svg',
        #                         output_field=models.ImageField(),
        #                     )
        #                 )
        #                 .order_by("-created_at")[:10]  
        #                 )
        recent_games = (
                        Game.objects.filter(
                            Q(player1=user) | Q(player2=user)
                        )
                        .select_related('player1', 'player2') 
                        .annotate(
                            user_score=Case(
                                When(player1=user, then=F("player1_score")),
                                When(player2=user, then=F("player2_score")),
                                default=Value(0),
                                output_field=IntegerField(),
                            ),
                            result=Case(
                                When(winner=user.id, then=Value("Win")),
                                default=Value("Loss"),
                                output_field=CharField(),
                            ),
                            opponent_avatar=Case(
                                When(player1=user, then=F("player2__avatar")),
                                When(player2=user, then=F("player1__avatar")),
                                default=Value('user.svg'),
                                output_field=CharField(), 
                                # output_field=models.ImageField(), 
                            ),
                        )
                        .order_by("-created_at")[:10]
                    )
        

        total_score = Game.objects.aggregate(
                                    total_score=Sum(
                                        Case(
                                            When(player1=user, then=F("player1_score")),
                                            When(player2=user, then=F("player2_score")),
                                            default=Value(0),
                                            output_field=IntegerField(),
                                        )
                                            )
                                            )['total_score']
                                
                                
        
        print("total solo games : ", total_solo_games)
        print("total_played_tournament : ", total_played_tournament)
        print("total_win_games : ", total_win_games)
        print("total_win_tournaments : ", total_win_tournaments)
        print("total_loss_games : ", total_loss_games)
        print("total_loss_tournaments : ", total_loss_tournaments)
        for game in recent_games:
            print("============")
            print(f"User Score: {game.user_score}")
            print(f"Result: {game.result}")
            print(f"Avatar: {game.opponent_avatar}")
            print(f"Created At: {game.created_at}")
        print("============")
        print("total score : ", total_score)

        response_data = {
                "avatar" : user.avatar.url[1:],
                "id" : user.id,
                "nickname" : user.nickname,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "total_solo_games": total_solo_games,
                "total_played_tournament": total_played_tournament,
                "total_win_games" : total_win_games,
                "total_win_tournaments" : total_win_tournaments, 
                "total_loss_games" : total_loss_games,
                "total_loss_tournaments" : total_loss_tournaments,
                'recent_games': list(recent_games.values('id', 'user_score', 'result', 'opponent_avatar')),
                "total_score" : total_score if total_score else 0
            }

        try:
            if hasattr(request, 'profile'):
                friendship = Friendship.objects.get(
                    (Q(user1=user) & Q(user2=request.user)) | (Q(user2=user) & Q(user1=request.user))
                )
                response_data['relationship'] = friendship.status
                response_data['last_action'] = friendship.last_action_by
        except Friendship.DoesNotExist:
            response_data['relationship'] = ''
            response_data['last_action'] = ''
        
        print('response::::::: ', response_data)
        return JsonResponse(response_data)

# from rest_framework.parsers import MultiPartParser, FormPars/er
from rest_framework.decorators import api_view

@api_view(['PATCH'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    print("UPDATE PROFILE")
    user = request.user
    data = request.data
    print('req: ', data)
    print("Request Files:", request.FILES)
    print('user avatar: ', user.avatar)
    # profile_instance = UserAccount.objects.get(user=request.user)
    print('user: ', user)
    ser = UserSerializer(instance=user, data=request.data, partial=True)
    if ser.is_valid():
        ins = ser.save()
        print('ins: ', ins.avatar)
        print('ser: ', ser.data)
        print('user.avat: ', user.avatar)
        print('user.url: ', user.avatar.url)
        return Response(ser.data)
    return Response({'error': 'zab'})






class UpdateProfile(APIView):
    # parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        
        print("UPDATE PROFILE")
        user = request.user
        data = request.data
        print('req: ', data)
        print("Request Files:", request.FILES)
        print('user avatar: ', user.avatar)


        ser = UserSerializer(instance=user, data=request.data, partial=True)
        # print('ser ok: ', ser.data)
        if ser.is_valid():
            ins = ser.save()
        first_name  = request.data.get('first_name')
        last_name  = request.data.get('last_name')
        email  = request.data.get('email')
        nickname  = request.data.get('nickname')
        avatar = request.data.get('avatar')

        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if nickname:
            user.nickname = nickname
            
        if avatar:
            user.avatar = avatar
        
        # print("first_name : ", first_name)
        # print("last_name : ", last_name)
        # print("email : ", email)
        # print("nickname : ", nickname)
        # print("avatar : ", avatar)

        try :
            user.full_clean()
            user.save()
            return Response({'message': 'User updated successfully.'}, status=status.HTTP_200_OK)

        except ValidationError as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)