import os
from datetime import datetime, timedelta
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework_jwt.views import refresh_jwt_token
from .service import AuthService
from .serializers import AuthUserSerializer
from .auth_classes import JWTAuthCookie
from users.service import UserService
from config.utils import get_env
from .utils import get_now_delta

from users.permissions import IsGasStationAdmin, IsSuperUser, IsCompanyAdmin

auth_service = AuthService()
user_service = UserService()


# To check if the provided acces_token is valid via default Auth class
# see config/settings.py > REST_FRAMEWORK
@api_view(["GET"])
def check(request):
    response = Response(data={"msg": "ok", "user": AuthUserSerializer(request.user).data})
    return response


# To check if the provided acces_token is valid via cookies
# see authentication/extra_auth_classes.py
@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@csrf_protect
def check_wapp(request):
    response = Response(data={"msg": "ok", "user": AuthUserSerializer(request.user).data})
    return response


## send Auth token (JWT) to Non web browser clients
## Handling the Auth token should be responsability of the client app
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def auth_local(request):
    identifier = request.data.get("identifier")  # can be email or user code
    password = request.data.get("password")
    if (not identifier) or (not password):
        raise exceptions.AuthenticationFailed("identifier and password required")

    user = auth_service.validate_user_by_credentials(identifier, password)
    if not user:
        raise exceptions.AuthenticationFailed("Wrong credentials")

    token, payload_data = auth_service.generate_jwt(user)
    response = Response(data={"token": token, "user": payload_data})

    return response


## Set Auth token (JWT) in Browser clients via cookies header.
## csrf prevention token is set in cookie
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def auth_local_wapp(request):
    identifier = request.data.get("identifier")
    password = request.data.get("password")

    if (not identifier) or (not password):
        raise exceptions.AuthenticationFailed("identifier and password required")

    user = auth_service.validate_user_by_credentials(identifier, password)
    if not user:
        raise exceptions.AuthenticationFailed("Wrong credentials")
    if not (user.is_admin or user.is_gas_station_admin):
        raise exceptions.AuthenticationFailed("Not authorized")

    token, payload_data = auth_service.generate_jwt(user)
    response = Response(data={"token": token, "user": payload_data})
    response.set_cookie(
        key=get_env("JWT_COOKIE_NAME"),
        value=token,
        httponly=True,
        secure=get_env("SECURE_COOKIE") == "True",
        samesite="None",
        expires=get_now_delta(days=3),
    )
    return response


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def logout_wapp(request):
    response = Response()
    response.delete_cookie(key=get_env("JWT_COOKIE_NAME"))
    return response

