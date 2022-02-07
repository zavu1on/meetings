import jwt
from datetime import datetime
from typing import Optional
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User, Token


class AuthBackend(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request, token=None, **kwargs) -> Optional[tuple]:
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != b'bearer':
            return None

        if len(auth_header) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credential provided.')
        elif len(auth_header) > 2:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. Token string should not contain spaces'
            )

        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeError:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. Token string should not contain invalid characters.'
            )

        return self.authenticate_credential(token)

    def authenticate_credential(self, token) -> tuple:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        except jwt.PyJWTError:
            raise exceptions.AuthenticationFailed('Invalid authentication. Could not decode token.')

        token_exp = datetime.fromtimestamp(payload['exp'])
        if token_exp < datetime.utcnow():
            Token.objects.get(token=token).delete()

            raise exceptions.AuthenticationFailed('Token expired.')

        try:
            token = Token.objects.get(
                token=token
            )
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Такой токен не зарегистрирован!')

        if token.user.id != payload['id']:
            raise exceptions.AuthenticationFailed('Вы используете чужой токен!')

        try:
            user = User.objects.get(id=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Такой пользователь не найден!')

        return user, None
