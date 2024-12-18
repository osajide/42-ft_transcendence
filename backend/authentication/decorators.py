from rest_framework.exceptions import PermissionDenied
import jwt
from .tokens import *
from .models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

def two_fa_required(view_func):
    def wrapper(request, *args, **kwargs):
        print("TWOFA CHECK")
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        user_id = token_decoder(raw_token)
        user = get_object_or_404(UserAccount, pk__in=user_id)
        # print("username : ", user.first_name)
        if (user.is_2fa_verified == False):
             return JsonResponse({"error": "2FA not verified. Please complete 2FA to proceed."}, status=403)
    return wrapper
