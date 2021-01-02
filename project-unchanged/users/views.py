import os
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.urls import reverse
from django.views.generic import View
from django.contrib import messages
import json
import requests

from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db.utils import IntegrityError
from rest_framework import exceptions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .service import UserService, RoleService, PermissionService, search_users, ResetPassword
from .permissions import IsGasStationAdmin, IsSuperUser, IsCompanyAdmin
from authentication.service import AuthService
from authentication.auth_classes import JWTAuthCookie
from config.utils import get_env
from .utils.permission_models import PERMISSION_MODELS
from .utils.password_generator import getPassword

auth_service = AuthService()
user_service = UserService()
role_service = RoleService()
reset_pass = ResetPassword()
permission_service = PermissionService()


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def signup(request):
	user = user_service.get_user(email=request.data.get("email"))
	if user:
		return Response(status=409, data={"type": "User already exist"})

	device = request.data.pop("device", None)

	created_user = user_service.create_user(request.data)
	try:
		user_service.create_user_balances(created_user)
	except:
		pass

	token, payload_data = auth_service.generate_jwt(created_user)
	response = Response(data={"token": token, "user": payload_data})
	return response


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def signup_facebook(request):
	token = request.data.get("token")
	if not token:
		raise exceptions.AuthenticationFailed("facebook access token is required")

	user_data = auth_service.get_facebook_user(token)
	if not user_data:
		raise exceptions.AuthenticationFailed("need to provide a valid facebook access token")

	user = user_service.get_user(email=user_data.get("email"))
	if not user:
		user = user_service.create_user(
			{
				"first_name": user_data.get("first_name"),
				"last_name": user_data.get("last_name"),
				"email": user_data.get("email"),
				# password is just in case.
				# Anyway to allow login with user/pass,
				# the "has_provided_password" flag should be True
				"password": token[-20:],
				"has_provided_password": False,
			}
		)
		try:
			user_service.create_user_balances(user)
		except:
			pass
	jwtoken, payload_data = auth_service.generate_jwt(user)
	response = Response(data={"token": jwtoken, "user": payload_data})
	return response



class BillingData(APIView):
	def get(self, request):
		billing_data = user_service.get_billing_data(request.user)
		return Response(data=billing_data)

	def put(self, request):
		try:
			updated_data = user_service.update_billing_data(request.user, request.data)
		except IntegrityError as e:
			key = e.__str__().split("'")[1]
			return Response(status=455, data={"error": key})
		return Response(data=updated_data)


class BalanceData(APIView):
	def get(self, request):
		station_id = request.GET.get("station_id")
		if station_id and station_id.isdigit():
			balance = user_service.get_balance(user=request.user, station_id=station_id)
			if not balance:
				return Response(
					status=status.HTTP_404_NOT_FOUND, data={"msg": "no hay balance"}
				)
			return Response(data={"balance": balance})

		balances = user_service.get_company_balances(user=request.user)
		return Response(data={"balances": balances})


@api_view(["GET"])
def get_vehicles(request):
	vehicles = user_service.get_vehicles(request.user)
	return Response(data={"vehicles": vehicles})


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_users_company(request):
	if request.user.is_admin:
		return Response(data=user_service.get_users_by_company(request.user))
	elif request.user.is_gas_station_admin:
		return Response(data=user_service.get_users_by_station(request.user))
	else:
		raise exceptions.APIException("User not allowed")



@api_view(["PUT"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsSuperUser | IsGasStationAdmin])
@csrf_exempt
def update_user(request):
	return Response(data=user_service.update_user_data(request.data))


@api_view(["GET"])
@cache_page(60 * 60 * 10)
def user_search(request):
	user = request.user
	text = request.GET.get("text")
	if not text or len(text) < 4:
		return Response(
			status=status.HTTP_400_BAD_REQUEST, data={"msg": "text empty or too short"}
		)
	results = search_users(text)

	return Response(data={"results": results})


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def reset_password(request):
	email = request.data.get("email")
	if not email:
		raise exceptions.AuthenticationFailed("email required")

	user = user_service.get_user(email=request.data.get("email"))
	# if not user:
	#    raise exceptions.AuthenticationFailed("wrong, don't exist that email")
	if user:
		reset_pass.send_email(user)

	return Response(status=200, data={"msg": "correo enviado"})


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def reset_password_done(request):
	return render(request, "reset/password_reset_done.html")


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def reset_password_error(request):
	return render(request, "reset/password_reset_error.html")


@api_view(["POST"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsSuperUser | IsGasStationAdmin])
def change_status(request):
    new_Status = request.data.get("new_status")
    email = request.data.get("email")
    return Response(data=user_service.change_status(email, new_Status))

class CompletePasswordReset(View):
	def get(self, request, uidb64, token):
		context = {"uidb64": uidb64, "token": token}

		try:
			id_user = force_text(urlsafe_base64_decode(uidb64))
			user = user_service.get_user(id=id_user)

			payload = reset_pass.verify_token(token)
			if not user or not payload:
				return redirect("reset-password-error")

			is_valid = reset_pass.verify_user_token_uidb(payload, user)
			if not is_valid:
				return redirect("reset-password-error")
		except Exception as identifier:
			pass

		return render(request, "reset/password_reset.html", context)

	def post(self, request, uidb64, token):
		context = {"uidb64": uidb64, "token": token}

		cedula = request.POST["cedula"]
		password = request.POST["password"]
		password2 = request.POST["password2"]

		if password != password2:
			messages.error(request, "Contraseñas no coinciden")
			return render(request, "reset/password_reset.html", context)

		if len(password) < 8:
			messages.error(request, "Contraseñas muy corta")
			return render(request, "reset/password_reset.html", context)

		try:
			id_user = force_text(urlsafe_base64_decode(uidb64))
			user = user_service.get_user(id=id_user)

			if cedula != user.cedula:
				messages.error(request, "Cedula incorrecta")
				return render(request, "reset/password_reset.html", context)

			payload = reset_pass.verify_token(token)
			if not user or not payload:
				return redirect("reset-password-error")

			# establecer la contraseña
			user.set_password(password)
			user.save()

			messages.success(request, "")
			return redirect("reset-password-done")
		except Exception as identifier:
			messages.info(request, "Ocurrio un problema, intente de nuevo")
			return render(request, "reset/password_reset.html", context)

