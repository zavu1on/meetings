from django.urls import path
from . import views

urlpatterns = [
    path('get/', views.GetMeetingsView.as_view()),
    path('create/', views.CreateMeetingView.as_view()),
    path('enter/', views.EnterToMeetingView.as_view()),
    path('delete/<slug:token>/', views.DelMeetingView.as_view()),
    path('images/get/', views.GetRoomImagesView.as_view()),
    path('data/get/<slug:token>/', views.GetMeetingData.as_view()),
    path('rooms/get/<slug:token1>/<slug:token2>/', views.GetRoomData.as_view()),
    path('rooms/add/<slug:token>/', views.AddRoomView.as_view()),
    path('rooms/delete/<slug:token>/', views.DelRoomView.as_view()),
]
