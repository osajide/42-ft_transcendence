from authentication.models import UserAccount
from channels.db import database_sync_to_async
from django.http import parse_cookie
from authentication.tokens import token_decoder
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user(user_id):
    try:
        return UserAccount.objects.get(id=user_id)
    except UserAccount.DoesNotExist:
        return AnonymousUser()

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
            print('access token not found')
            scope['user'] = AnonymousUser()
        else:
            access_token = cookie['access_token']
            user_id = token_decoder(access_token)
            scope['user'] = await get_user(user_id)

        return await self.app(scope, receive, send)