from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

from rest_framework_simplejwt.tokens import AccessToken

from App.models import User


@database_sync_to_async
def get_user(token):

    try:

        access_token = AccessToken(token)

        user_id = access_token["user_id"]

        return User.objects.get(id=user_id)

    except Exception:

        return None


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = scope["query_string"].decode()

        query_params = parse_qs(query_string)

        token = query_params.get("token")

        if token:

            token = token[0]

            user = await get_user(token)

            scope["user"] = user

        else:

            scope["user"] = None

        return await super().__call__(
            scope,
            receive,
            send
        )