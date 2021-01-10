import os
from rest_framework import exceptions
from django.utils.encoding import smart_text
from users.models import User
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from config.utils import get_env


# Authentication method with JWT via HTTP Header -> Authorization: Bearer <JWT>
# It's used on views for the mobile client only
class JWTAuth(JSONWebTokenAuthentication):
	def authenticate_credentials(self, payload):
		payload.pop("exp", None)
		payload.pop("orig_iat", None)
		payload.pop("username", None)
		payload["id"] = payload.pop("user_id", None)
		user = User(**payload)
		if not user.is_active:
			raise exceptions.AuthenticationFailed("User account is disabled.")
		return user

# Authentication method with JWT via COOKIES
# It's used on views for web-browser clients only, and should be used alongside CSRF protection token 
# which can be set on cookies too.
class JWTAuthCookie(JWTAuth):
	def get_jwt_value(self, request):
		jwt_cookie_name = get_env("JWT_COOKIE_NAME")
		return request.COOKIES.get(jwt_cookie_name, "nope")

