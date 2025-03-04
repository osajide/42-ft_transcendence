from authentication.models import UserAccount
from channels.db import database_sync_to_async
from django.http import parse_cookie
from authentication.tokens import token_decoder
from django.contrib.auth.models import AnonymousUser
import jwt 
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import re
from asgiref.sync import sync_to_async

# ------------------------ from channels/auth.py ----------------------------------

class CookiesMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        cookie = ""
        headers = scope['headers']
        for key, value in headers:
            if key == b'cookie':
                cookie = value.decode('utf-8')
        cookie = parse_cookie(cookie)
        if not 'access_token' in cookie:
            print('cookies: ************: ', cookie)
            print('access token not found')
            scope['user'] = AnonymousUser()
        else:
            try:
                payload = jwt.decode(cookie['refresh_token'], settings.SECRET_KEY, algorithms=['HS256'])
                jwt.decode(cookie['access_token'], settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            except jwt.ExpiredSignatureError:
                print("refresh token expired")
                scope['user'] = AnonymousUser()
                return await self.app(scope, receive, send)
            except jwt.InvalidTokenError:
                print("invalid access token")
                scope['user'] = AnonymousUser()
                return await self.app(scope, receive, send)
            access_token = cookie['access_token']
            decoded_data = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            user_id = decoded_data['user_id']
            scope['user'] = await sync_to_async(UserAccount.objects.get)(id__in=user_id)
            print("CONNECTED USER : ", scope['user'].last_name)
        return await self.app(scope, receive, send)
    
# ---------------------     from rest_framework_simplejwt/authentication.py ------------------------------

from typing import Optional, Set, Tuple, TypeVar

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, authentication
from rest_framework.request import Request

from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework.exceptions import APIException

# from .tet import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings
from .tokens import Token
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.tokens import AccessToken
import jwt
from authentication.models import UserAccount
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.response import Response

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES

if not isinstance(api_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES: Set[bytes] = {
    h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES
}

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class JWTAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def authenticate_header(self, request: Request) -> str:
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_header(self, request: Request) -> bytes:
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(api_settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header: bytes) -> Optional[bytes]:
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )

        return parts[1]

    def get_validated_token(self, raw_token: bytes) -> Token:
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    def get_user(self, validated_token: Token) -> AuthUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM
            ) != get_md5_hash_password(user.password):
                raise AuthenticationFailed(
                    _("The user's password has been changed."), code="password_changed"
                )

        return user


class JWTStatelessUserAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header without performing a database lookup to obtain a user instance.
    """

    def get_user(self, validated_token: Token) -> AuthUser:
        """
        Returns a stateless user object which is backed by the given validated
        token.
        """
        if api_settings.USER_ID_CLAIM not in validated_token:
            # The TokenUser class assumes tokens will have a recognizable user
            # identifier claim.
            raise InvalidToken(_("Token contained no recognizable user identification"))

        return api_settings.TOKEN_USER_CLASS(validated_token)


JWTTokenUserAuthentication = JWTStatelessUserAuthentication


def default_user_authentication_rule(user: AuthUser) -> bool:
    # Prior to Django 1.10, inactive users could be authenticated with the
    # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
    # prevents inactive users from authenticating.  App designers can still
    # allow inactive users to authenticate by opting for the new
    # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
    # users from authenticating to enforce a reasonable policy and provide
    # sensible backwards compatibility with older Django versions.
    return user is not None and user.is_active


class TokenBlacklistedException(Exception):
    pass

class CustomAuthenticationError(APIException):
    status_code = 401
    default_detail = {'error': 'Invalid authentication credentials.'}
    default_code = 'authentication_failed'

    def __init__(self, error=None):
        if error is not None:
            self.detail = {'error': error}
            
class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that retrieves the token from cookies.
    """
        
    def get_user(self, validated_token):
        """
        Override this method to retrieve the user from the JWT token payload.
        """
        try:
            # Assuming the user_id is stored in the token payload as 'user_id'
            user_id = validated_token['user_id']
            print("jti : ", validated_token['jti'])
            # token = BlacklistedToken.objects.filter(token=validated_token)
            # blacklisted_tokens = BlacklistedToken.objects.all()

            # # Print the JTI of each blacklisted token
            # print("Blacklisted Tokens:")
            # for blacklisted_token in blacklisted_tokens:
            #     print(f"JTI: {blacklisted_token.token.jti}")
                # raise TokenBlacklistedException()
            return UserAccount.objects.get(id__in=user_id)  # Look up the user by id in your custom model
        # except TokenBlacklistedException:
        #     print("banned token")
        #     raise AuthenticationFailed({'error' :'Banned Token'})
        except UserAccount.DoesNotExist:
            raise CustomAuthenticationError('User not found')
            # raise AuthenticationFailed({'error' :'User not found'})
        
        except KeyError:
            raise CustomAuthenticationError('User not found')
            # raise AuthenticationFailed({'error' :'Token does not contain user identifier'})
    
    def authenticate(self, request):
        # Retrieve the token from the cookie
        print("======HEREEE")
        raw_token = request.COOKIES.get('access_token')
        ref_token = request.COOKIES.get('refresh_token')
        if raw_token is None:
            return None
        if ref_token is None:
            return None


        # print("Blacklisted Tokens:")
        blacklisted_tokens = BlacklistedToken.objects.all()
        try:
            token = jwt.decode(ref_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            raise CustomAuthenticationError('Session expired!')

        for blacklisted_token in blacklisted_tokens:
            if blacklisted_token.token.jti == token['jti']:
                raise CustomAuthenticationError('Banned Token')

        validated_token = self.get_validated_token(raw_token)

        user = self.get_user(validated_token)

        print("GET USER INFO")
        print("user id : ", user.id)
        print("user email : ", user.email)
        return user, validated_token

    def get_validated_token(self, raw_token):
        """
        Validate the raw token using the configured secret and algorithm.
        """
        try:
            # Use AccessToken to validate the token
            # validated_token = AccessToken(raw_token)
            token = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            raise CustomAuthenticationError('Invalid access token')
        # except jwt.ExpiredSignatureError:
        #     raise AuthenticationFailed('Token has expired')
        
        return token
