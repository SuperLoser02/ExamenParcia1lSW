from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/diagrama/<int:diagrama_id>/", consumers.DiagramaConsumer.as_asgi()),
]
