"""
ASGI config for primer_parcial project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import diagrama.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "primer_parcial.settings")
django.setup()

from diagrama.middleware import JWTAuthMiddleware
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(diagrama.routing.websocket_urlpatterns)
    ),
})

