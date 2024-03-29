"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()

from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
import api.meetings.routing
import jwt
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from api.oauth.models import Token


@database_sync_to_async
def get_user(token):
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM, options={
            'verify_signature': True,
            'verify_exp': True
        })
        token = Token.objects.get(token=token)

        return token.user
    except:
        return AnonymousUser()


class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope['user'] = await get_user(scope['path'].split('/')[-2])

        return await self.app(scope, receive, send)


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddleware(
        URLRouter(
            api.meetings.routing.websocket_urlpatterns
        )
    ),
})
