from rest_framework import serializers
from api.oauth.models import User
from . import models


class CreateMeetingSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150, allow_null=True)
    room = serializers.IntegerField()
    room_name = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic']


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RoomImage
        fields = ['id', 'name', 'preview_image']


class RoomSerializer(serializers.ModelSerializer):
    room_image = RoomImageSerializer(read_only=True)

    class Meta:
        model = models.Room
        fields = '__all__'


class ListMeetingSerializer(serializers.ModelSerializer):
    owners = UserSerializer(read_only=True, many=True)

    class Meta:
        model = models.Meeting
        exclude = ['password', 'customers', 'rooms', 'black_list']


class EnterToMeetingSerializer(serializers.Serializer):
    url = serializers.CharField()
    password = serializers.CharField(allow_null=True)
