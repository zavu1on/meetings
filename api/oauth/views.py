import uuid
import jwt
from datetime import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from . import services
from .models import Token, User, RegistrationUserData, RecoverUserPasswordData
# Create your views here.
# todo добавить авторизацию через соц. сети


class RegistrationView(APIView):

    def post(self, request: Request):
        registration_serializer = serializers.RegistrationSerializer(data=request.data)

        if registration_serializer.is_valid():
            data = registration_serializer.initial_data

            try:
                User.objects.get(Q(username=data['username']) | Q(email=data['email']))

                return Response({'detail': 'Пользователь с таким именем или email уже существует!'}, 400)
            except User.DoesNotExist:
                pass

            registration_serializer.save(uuid=uuid.uuid1())

            data = registration_serializer.data

            send_mail(
                'Подтверждение регистрации',
                f'Для завершения регистрации пройдите по ссылке: {request.build_absolute_uri("/")}commit'
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

        login(request, user)
        resp = services.authenticate(user)

        Token.objects.create(
            token=resp['access_token'],
            user=user
        )

        return Response(resp, 201)


class LoginView(APIView):

    def post(self, request: Request):
        login_serializer = serializers.LoginSerializer(data=request.data)

        if login_serializer.is_valid():
            data = login_serializer.data

            user = authenticate(username=data['username'], password=data['password'])

            if user is None:
                return Response({'detail': 'Пользователь не найден!'}, 400)

            login(request, user)
            resp = services.authenticate(user)

            Token.objects.create(
                token=resp['access_token'],
                user=user
            )

            return Response(resp, 201)

        return Response({'serialize_error': login_serializer.errors}, 406)


class RefreshTokenView(APIView):

    def post(self, request: Request):
        token_serializer = serializers.RefreshTokenSerializer(data=request.data)

        if token_serializer.is_valid():
            try:
                payload = jwt.decode(token_serializer.data['token'], settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            except jwt.PyJWTError:
                return Response('Invalid authentication. Could not decode token.', 400)

            token_exp = datetime.fromtimestamp(payload['exp'])
            if token_exp < datetime.utcnow():
                return Response({'detail': 'Токен повтора истек, необходима повторная авторизация!'}, 400)

            try:
                user = User.objects.get(id=payload['id'])
                resp = services.authenticate(user)

                Token.objects.create(
                    token=resp['access_token'],
                    user=user
                )

                return Response(resp)
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
                return Response({'detail': 'Пользователь с таким именем или email не существует!'}, 404)

            serializer.save(uuid=uuid.uuid1(), user=user)
            data = serializer.data

            send_mail(
                'Восстановление пароля',
                f'Для восстановления пароля перейдите по ссылке: {request.build_absolute_uri("/")}commit'
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

        return Response({})
