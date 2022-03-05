import jwt
from random import random
from datetime import datetime, timedelta
from django.conf import settings
from .models import User, Token


def authenticate(user: User) -> dict:
    access_token = jwt.encode(
        {
            'id': user.id,
            'type': 'access',
            'random_key': datetime.utcnow().timestamp() * random(),
            'exp': datetime.utcnow() + timedelta(minutes=30),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    refresh_token = jwt.encode(
        {
            'id': user.id,
            'type': 'refresh',
            'random_key': datetime.utcnow().timestamp() * random(),
            'exp': datetime.utcnow() + timedelta(weeks=1)
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    Token.objects.create(
        token=access_token,
        user=user
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
