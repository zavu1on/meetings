import uuid
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from . import models
# Create your views here.


class CreateMeetingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = serializers.CreateMeetingSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data

            m = models.Meeting.objects.create(
                name=data['name'],
                password=data['password'],
                slug=uuid.uuid1()
            )
            m.rooms.add(models.Room.objects.create(room_image_id=data['room'], slug=uuid.uuid1(), name=data['room_name']))
            m.owners.add(request.user)
            m.save()

            return Response({'meeting': serializers.ListMeetingSerializer(m).data}, 201)

        return Response({'serialize_error': serializer.errors}, 406)


class GetMeetingsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ListMeetingSerializer

    def get_queryset(self):
        return models.Meeting.objects.filter(owners__in=[self.request.user])


class GetRoomImagesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.RoomImageSerializer
    queryset = models.RoomImage.objects.all()


class EnterToMeetingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = serializers.EnterToMeetingSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data

            try:
                meeting = models.Meeting.objects.get(slug=data['url'], owners__in=[request.user])
                meeting.customers.add(request.user)

                return Response(status=204)
            except models.Meeting.DoesNotExist:
                pass
            try:
                meeting = models.Meeting.objects.get(slug=data['url'], password=data['password'])
            except models.Meeting.DoesNotExist:
                return Response({'detail': 'Встреча не найдена'}, 404)

            if request.user in meeting.black_list.all():
                return Response({'detail': 'Вы не можете зайти на конференцию'}, 400)

            meeting.customers.add(request.user)

            return Response(status=204)

        return Response({'serialize_error': serializer.errors}, 406)


class GetMeetingData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, token: str):
        try:
            meeting = models.Meeting.objects.get(slug=token)
        except models.Meeting.DoesNotExist:
            return Response({'detail': 'Такая конференция не найдена'}, 404)

        if request.user in meeting.black_list.all():
            return Response({'detail': 'Вы не можете зайти на конференцию'}, 400)

        return Response({
            'name': meeting.name,
            'rooms': serializers.RoomSerializer(meeting.rooms.all(), many=True).data,
            'isHost': request.user in meeting.owners.all()
        })


class DelMeetingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token: str):
        try:
            meeting = models.Meeting.objects.get(slug=token)

            if request.user not in meeting.owners.all():
                return Response({'detail': 'Вы не выполнить это действие'}, 400)
        except models.Meeting.DoesNotExist:
            return Response({'detail': 'Такая конференция не найдена'}, 404)

        meeting.delete()

        return Response(status=204)


class AddRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token: str):
        try:
            meeting = models.Meeting.objects.get(slug=token)

            if request.user not in meeting.owners.all():
                return Response({'detail': 'Вы не выполнить это действие'}, 400)
        except models.Meeting.DoesNotExist:
            return Response({'detail': 'Такая конференция не найдена'}, 404)

        room = models.Room.objects.create(room_image=models.RoomImage.objects.get(id=request.data['id']), slug=uuid.uuid1(), name=request.data['name'])
        meeting.rooms.add(room)

        return Response({
            'room': serializers.RoomSerializer(room).data,
        }, 201)


class DelRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token: str):
        try:
            meeting = models.Meeting.objects.get(slug=token)

            if request.user not in meeting.owners.all():
                return Response({'detail': 'Вы не выполнить это действие'}, 400)
        except models.Meeting.DoesNotExist:
            return Response({'detail': 'Такая конференция не найдена'}, 404)

        meeting.rooms.get(id=request.data['id']).delete()

        return Response(status=204)


class GetRoomData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, token1: str, token2: str):
        try:
            meeting = models.Meeting.objects.get(slug=token1)
        except models.Meeting.DoesNotExist:
            return Response({'detail': 'Такая конференция не найдена'}, 404)

        if request.user in meeting.black_list.all():
            return Response({'detail': 'Вы не можете зайти на конференцию'}, 400)

        try:
            room = meeting.rooms.get(slug=token2)
        except models.Room.DoesNotExist:
            return Response({'detail': 'Такая комната не найдена'}, 404)

        return Response({
            **serializers.RoomSerializer(room).data,
            'is_admin': request.user in meeting.owners.all()
        })
