# diagrama/middleware.py
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.middleware import BaseMiddleware

@database_sync_to_async
def get_user_from_token(token):
    try:
        validated_token = UntypedToken(token)
        user = JWTAuthentication().get_user(validated_token)
        #print(f"✅ Middleware: Usuario autenticado -> {user}")
        return user
    except Exception as e:
        #print(f"⚠️ Middleware: Token inválido -> {e}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token")

        if token_list:
            token = token_list[0]
            user = await get_user_from_token(token)
            scope["user"] = user
            if isinstance(user, AnonymousUser):
                print("⚠️ Middleware: Usuario no autenticado (AnonymousUser)")
        else:
            scope["user"] = AnonymousUser()
            print("⚠️ Middleware: No se pasó token en query string")

        return await super().__call__(scope, receive, send)
