from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('meetings/moving/<slug:token1>/<slug:token2>/<str:jwt>/', consumers.RoomConsumer.as_asgi()),
]
