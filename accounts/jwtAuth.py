import time

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions


def get_authorization_header(request):
    auth = request.META.get("HTTP_AUTHORIZATION")
    return auth


class JwtTokenAuthentication:
    def authenticate(self, request):
        token = get_authorization_header(request)
        if not token:
            return
        token = token.replace("jwt ", "")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
        user_id = payload.get("user_id")
        curTime = int(time.time())
        if (curTime > payload.get("exp")) or not user_id:
            return

        try:
            user = get_user_model().objects.get(pk=user_id)
        except:
            raise exceptions.AuthenticationFailed("사용자가 존재하지 않습니다.")

        return user, token
