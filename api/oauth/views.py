import uuid
import jwt
import requests
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files import File
from django.core.mail import send_mail
from django.db.models import Q
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from . import services
from .models import User, RegistrationUserData, RecoverUserPasswordData
# Create your views here.


class RegistrationView(APIView):

    def post(self, request: Request):
        registration_serializer = serializers.RegistrationSerializer(data=request.data)

        if registration_serializer.is_valid():
            data = registration_serializer.initial_data

            if len(User.objects.filter(Q(username=data['username']) | Q(email=data['email']))) != 0:
                return Response({'detail': 'Пользователь с таким именем или email уже существует!'}, 400)

            registration_serializer.save(uuid=uuid.uuid1())

            data = registration_serializer.data

            send_mail(
                'Подтверждение регистрации',
                f'Для завершения регистрации пройдите по ссылке: {request.build_absolute_uri("/")}#/commit'
                f'-registration/{data["uuid"]}/',
                settings.EMAIL_HOST_USER,
                [data['email']]
            )

            return Response(status=201)

        return Response({'serialize_error': registration_serializer.errors}, 406)


class CommitRegistrationView(APIView):

    def post(self, request: Request, uuid: str):
        try:
            data = RegistrationUserData.objects.get(uuid=uuid)
        except RegistrationUserData.DoesNotExist:
            return Response({'detail': 'Такой ключ не найден!'}, 404)

        user = User.objects.create(
            username=data.username,
            email=data.email,
            password=make_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            patronymic=data.patronymic,
        )
        data.delete()

        return Response(services.authenticate(user), 201)


class LoginView(APIView):

    def post(self, request: Request):
        login_serializer = serializers.LoginSerializer(data=request.data)

        if login_serializer.is_valid():
            data = login_serializer.data

            try:
                user = User.objects.get(username=data['username'])

                if not user.check_password(data['password']):
                    raise User.DoesNotExist

            except User.DoesNotExist:
                return Response({'detail': 'Пользователь не найден!'}, 404)

            return Response(services.authenticate(user), 201)

        return Response({'serialize_error': login_serializer.errors}, 406)


class RefreshTokenView(APIView):

    def post(self, request: Request):
        token_serializer = serializers.RefreshTokenSerializer(data=request.data)

        if token_serializer.is_valid():
            try:
                payload = jwt.decode(token_serializer.data['token'], settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            except jwt.PyJWTError:
                return Response('Токен повтора истек, необходима повторная авторизация!', 400)

            token_exp = datetime.fromtimestamp(payload['exp'])
            if token_exp < datetime.utcnow():
                return Response({'detail': 'Токен повтора истек, необходима повторная авторизация!'}, 400)

            try:
                user = User.objects.get(id=payload['id'])

                return Response(services.authenticate(user))
            except User.DoesNotExist:
                return Response({'detail': 'Такой пользователь не найден!'}, 400)

        return Response({'serialize_error': token_serializer.errors}, 406)


class RecoverPasswordView(APIView):

    def post(self, request: Request):
        serializer = serializers.RecoverPasswordSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.initial_data

            try:
                user = User.objects.get(username=data['username'], email=data['email'])
            except User.DoesNotExist:
                return Response({'detail': 'Пользователь с таким именем или email не найден!'}, 404)

            serializer.save(uuid=uuid.uuid1(), user=user)
            data = serializer.data

            send_mail(
                'Восстановление пароля',
                f'Для восстановления пароля перейдите по ссылке: {request.build_absolute_uri("/")}#/commit'
                f'-recover-password/{data["uuid"]}/',
                settings.EMAIL_HOST_USER,
                [data['email']]
            )

            return Response(status=201)

        return Response({'serialize_error': serializer.errors}, 406)


class CommitRecoverPasswordView(APIView):

    def post(self, request: Request, uuid: str):
        try:
            data = RecoverUserPasswordData.objects.get(uuid=uuid)
        except RecoverUserPasswordData.DoesNotExist:
            return Response({'detail': 'Такой ключ не найден!'}, 404)

        data.user.set_password(request.data['password'])
        data.user.save()
        data.delete()

        return Response(status=204)


class GoogleAuthView(APIView):

    def post(self, request: Request):
        serializer = serializers.GoogleAuthSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data

            try:
                google_data = id_token.verify_oauth2_token(data['token'], GoogleRequest())
            except ValueError:
                return Response({'detail': 'Не можем авторизовать google аккаунт!'}, 500)

            try:
                user = User.objects.get(email=google_data['email'])

                return Response(services.authenticate(user))
            except User.DoesNotExist:
                password = str(uuid.uuid1())
                resp = requests.get(google_data['picture'])

                user = User.objects.create(
                    username=google_data['email'].split('@')[0],
                    email=google_data['email'],
                    password=make_password(password),
                    first_name=google_data['given_name'],
                    last_name=google_data['family_name'],
                )

                user.avatar.save(
                    content=File(BytesIO(resp.content)),
                    name=f"{google_data['email'].split('@')[0]}.{datetime.utcnow()}.jpg"
                )
                user.save()

                user.email_user(
                    'Сгенерированный пароль',
                    f'Вы авторизовались через аккаунт google, ваш пароль от аккаунта - {password}, Вы всегда можете поменять его!',
                    settings.EMAIL_HOST_USER
                )

                return Response(services.authenticate(user), 201)

        return Response({'serialize_error': serializer.errors}, 406)


class GetUserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):

        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'fullName': request.user.get_full_name(),
            'avatarUrl': request.build_absolute_uri("/") + request.user.avatar.url.replace('/', '', 1),
        })


class SetUserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        request.user.avatar = request.FILES['avatar']
        request.user.save()

        return Response({'avatarUrl': request.build_absolute_uri("/") + request.user.avatar.url.replace('/', '', 1)})
