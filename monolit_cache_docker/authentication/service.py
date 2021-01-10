## business logic quering
## All data manipulation should be done here
## avoid doing data manipulation on django views
import os
import jwt
import requests
from datetime import datetime, timedelta
from users.models import User
from .serializers import AuthUserSerializer
from django.db.models import Model
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings
from config.utils import get_env

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class AuthService:
    def __init__(self):
        self.whatever = "whatever"

    def generate_jwt(self, user):
        payload = jwt_payload_handler(user)
        payload["username"] = payload.get("email")
        payload["first_name"] = user.first_name
        payload["last_name"] = user.last_name
        payload["cedula"] = user.cedula
        payload["is_active"] = user.is_active
        payload["is_gas_station_admin"] = user.is_gas_station_admin
        payload["is_superuser"] = user.is_superuser
        payload["is_admin"] = user.is_admin
        token = jwt_encode_handler(payload)
        return token, payload

    def refresh_jwt(self, token):
        return None

    def validate_user_by_credentials(self, identifier, password):
        user = None
        try:
            if identifier.isdigit():
                user = User.objects.get(id=int(identifier))
            else:
                user = User.objects.get(email=identifier)
        except:
            raise exceptions.AuthenticationFailed("User do not exist")

        if user:
            if not user.has_provided_password:
                raise exceptions.AuthenticationFailed(
                    "User is not allowed to perform this task"
                )
            if user.check_password(password):
                return user
        return None

    def validate_facebook_token(self, token):
        res = requests.get(
            "https://graph.facebook.com/debug_token",
            params={
                "input_token": token,
                "access_token": f'{get_env("FACEBOOK_APP_ID")}|{get_env("FACEBOOK_APP_SECRET")}',
            },
        )
        if res.status_code >= 400:
            return False
        return res.json().get("data", {}).get("is_valid")

    def get_facebook_user(self, user_access_token):
        res = requests.get(
            "https://graph.facebook.com/v8.0/me",
            params={
                "fields": "email,name,first_name,last_name",
                "access_token": user_access_token,
            },
        )
        if res.status_code >= 400 or res.json().get("error"):
            return None
        return res.json()
