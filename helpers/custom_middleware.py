import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class TokenAuthMiddleware(BaseMiddleware):  # type: ignore
    def __init__(self, inner):  # type: ignore
        super().__init__(inner)

    async def __call__(self, scope, receive, send):  # type: ignore
        try:
            token = self.get_token_from_scope(scope)  # type: ignore
            user = await self.get_user_from_token(token)
            scope["user"] = user
        except:
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):  # type: ignore
        headers = dict(scope["headers"])
        # headers는 bytes 형태로 전달되므로 디코딩 필요
        auth_header = headers.get(b"authorization", b"").decode()

        if not auth_header.startswith("Bearer "):
            raise ValueError("Invalid authorization header")

        token = auth_header.split(" ")[1]
        return token

    @database_sync_to_async
    def get_user_from_token(self, token):  # type: ignore
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
            User = get_user_model()
            return User.objects.get(id=user_id)
        except:
            return AnonymousUser()[1][2]  # type: ignore
