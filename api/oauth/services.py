import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import User


def authenticate(user: User) -> dict:
    access_token = jwt.encode(
        {
            'id': user.id,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=30),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    refresh_token = jwt.encode(
        {
            'id': user.id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(weeks=1)
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
