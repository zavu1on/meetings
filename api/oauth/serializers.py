from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import RegistrationUserData, RecoverUserPasswordData


class LoginSerializer(Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150)


class RefreshTokenSerializer(Serializer):
    token = serializers.CharField()


class RegistrationSerializer(ModelSerializer):
    class Meta:
        model = RegistrationUserData
        fields = '__all__'


class RecoverPasswordSerializer(ModelSerializer):
    class Meta:
        model = RecoverUserPasswordData
        fields = '__all__'


class GoogleAuthSerializer(Serializer):
    token = serializers.CharField()
    password = serializers.CharField()
