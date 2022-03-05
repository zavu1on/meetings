from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.oauth.urls')),
    path('meetings/', include('api.meetings.urls')),
]
