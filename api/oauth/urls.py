from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.RegistrationView.as_view()),
    path('commit-registration/<str:uuid>/', views.CommitRegistrationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('refresh-token/', views.RefreshTokenView.as_view()),
    path('recover-password/', views.RecoverPasswordView.as_view()),
    path('commit-recover-password/<str:uuid>/', views.CommitRecoverPasswordView.as_view()),
    path('google/', views.GoogleAuthView.as_view()),
    path('get-user-data/', views.GetUserDataView.as_view()),
    path('set-user-avatar/', views.SetUserAvatarView.as_view()),
]
