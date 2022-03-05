import jwt
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
                'Invalid token header. Token string should not contain invalid characters.',
            )

        return self.authenticate_credential(token)

    def authenticate_credential(self, token) -> tuple:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM, options={
                'verify_signature': True,
                'verify_exp': True
            })
        except jwt.PyJWTError:
            raise exceptions.AuthenticationFailed('Invalid authentication. Could not decode token.')

        try:
            t = Token.objects.get(token=token)

            if t.user.id != payload['id']:
                raise exceptions.AuthenticationFailed('Вы используете чужой токен!')
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Такой токен не зарегистрирован!')

        try:
            user = User.objects.get(id=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Такой пользователь не найден!')

        return user, None
