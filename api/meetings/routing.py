from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('meetings/moving/<slug:token1>/<slug:token2>/<str:jwt>/', consumers.MovingConsumer.as_asgi()),
]
