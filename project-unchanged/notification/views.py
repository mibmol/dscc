from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from users.models import User
from users.service import UserService
from notification.notification_provider import (
	register_user_device_token,
	delete_user_device_token,
)
from notification.notification_provider import get_notifications_new, get_notifications_old

user_service = UserService()


class UserToken(APIView):
	def post(self, request):
		device_info = request.data.get("device_info")
		if not device_info or not device_info.get("token"):
			return Response(
				status=status.HTTP_401_UNAUTHORIZED, data={"msg": "No device info"}
			)
		user = user_service.get_user(id=request.user.id)
		if not user:
			return Response(
				status=status.HTTP_401_UNAUTHORIZED, data={"msg": "Bad identifier"}
			)
		register_user_device_token(user, device=device_info)
		return Response(status=status.HTTP_200_OK, data={"ok": "ok"})

	def delete(self, request):
		token = request.GET.get("token")
		if not token:
			return Response(
				status=status.HTTP_400_BAD_REQUEST, data={"msg": "Missing param 'token"}
			)
		user = user_service.get_user(id=request.user.id)
		if not user:
			return Response(
				status=status.HTTP_401_UNAUTHORIZED, data={"msg": "Bad identifier"}
			)
		delete_user_device_token(user, token=token)
		return Response(status=status.HTTP_200_OK, data={"ok": "ok"})


@api_view(['GET'])
def notifications(request):
	result = get_notifications_new(request.user)
	return Response(data={'notifications': result})

@api_view(['GET'])
def notifications_old(request):
	last = request.GET.get('last')
	if not last or not last.isdigit():
		return Response(data={'notifications': []})	
	result = get_notifications_old(request.user, int(last))
	return Response(data={'notifications': result})

