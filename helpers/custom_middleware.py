import logging
from urllib.parse import parse_qs

import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class TokenAuthMiddleware(BaseMiddleware):  # type: ignore
    def __init__(self, inner):  # type: ignore
        super().__init__(inner)

    async def __call__(self, scope, receive, send):  # type: ignore
        logger.info(f"WebSocket 연결 요청: {scope}")
        try:
            token = self.get_token_from_scope(scope)  # type: ignore
            user = await self.get_user_from_token(token)
            scope["user"] = user
        except:
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):  # type: ignore
        query_string = parse_qs(scope["query_string"].decode())

        # 🔹 URL 쿼리 파라미터에서 토큰 가져오기
        token = query_string.get("token", [None])[0]

        if not token:
            raise ValueError("Missing token")

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
