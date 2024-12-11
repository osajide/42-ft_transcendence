from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from .models import UserAccount
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserAccount
from .tokens import get_tokens_for_user
from rest_framework import status

class GetAuthCode(APIView):
    def get(request, provider):

        url =  'https://api.intra.42.fr/oauth/authorize'
        params = {
            "client_id" : 'u-s4t2ud-1619f031b401b49c5796f0b7dc500bab1bad5c24ab3c19bb97df8c83adbfc15f',
            "redirect_uri" : "http://127.0.0.1:8000/api/intra/oauth/",
            "response_type": "code",
            "scope": 'public',
            "prompt": "consent",
        }

        auth_url = requests.Request('GET', url, params=params).prepare().url
        return redirect(auth_url)


def register_new_user(user_data):

    print("USER EMAIL :", user_data['email'])
    user = UserAccount.objects.filter(email=user_data['email'])

    if not user:

        # after set the username also

        # auth_username = user.username
        # while UserAccount.objects.filter(username=username).exists():
        #     username = auth_username + '_'

        user = UserAccount.objects.create(email=user_data['email'], first_name=user_data['first_name'], last_name=user_data['last_name'])
        user.set_unusable_password()
        user.save()
    else:
        return ({'error': 'email already in use for login.'})

    tokens = get_tokens_for_user(user)

    return {
        'email': user.email,
        'access_token': tokens['access'],
        'refresh_token': tokens['refresh']
    }

class OAuthCallback(APIView):
    def get(request, code):
        
        #provide to the resource server the data to get access token
        code = code.GET.get('code')

        
        print("code =>", code)
        if code is None:
            return Response({'No code is provided'})
        url = 'https://api.intra.42.fr/oauth/token'
        data = {
            "grant_type": "authorization_code",
            "client_id": 'u-s4t2ud-1619f031b401b49c5796f0b7dc500bab1bad5c24ab3c19bb97df8c83adbfc15f',
            "client_secret": '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',
            "code": code,
            "redirect_uri" : "http://127.0.0.1:8000/api/intra/oauth/",
        }
        

        response = requests.post(url, data=data)

        token_data = response.json()
        if response.status_code != 200:
            return Response({'Failed to exchange code for token'})

        #get access token and send it to the intra to get the user data 

        access_token = token_data.get('access_token')

        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        user_data = response.json()

        #resgistring the user and create for it access and refresh token 

        #in the front end you will get the access token and save it locally
        result = register_new_user(user_data)
        print('error' in result)
        if 'error' in result:
            return Response({'error': 'email already in use for login.'})
        

        response =  Response({result['email']}, status=status.HTTP_201_CREATED)
        

        response.set_cookie('refresh_token', result['refresh_token'], httponly=True, samesite='None', secure=True)
        response.set_cookie('access_token', result['access_token'], httponly=True, samesite='None', secure=True)
        response = HttpResponseRedirect('http://127.0.0.1:5500/')
        return response

