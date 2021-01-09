## business logic quering
## All data manipulation should be done here
## avoid doing it on django views
from rest_framework.exceptions import APIException, ValidationError
from .models import User
from .serializers import (
	CreateUserSerializer,
	CreateUserAdminSerializer,
	GetUserSerializer,
	UpdateBillingDataSerializer,
	UserResultSerializer,
)

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import exceptions, serializers
from company.models import GasStation, Company
from django.contrib.auth.models import Group
from .utils.utils import remove_key_from_list

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes, force_text
from django.urls import reverse
from datetime import datetime, timedelta
import json
import requests
import jwt

from scripts.validate import validate_date_range

from config.utils import get_env

RESTDB_MAIL_HOST = get_env("RESTDB_MAIL_HOST")
RESTDB_API_KEY = get_env("RESTDB_API_KEY")
HOST_ACTUAL = get_env("HOST_ACTUAL")
JWT_SECRET = get_env('JWT_SECRET')
JWT_ALGORITHM = get_env('JWT_ALGORITHM')
JWT_EXP_DELTA_SECONDS = get_env('JWT_EXP_DELTA_SECONDS')

class UserService:
	def __init__(self):
		self.whatever = "whatever"

	def get_user(self, id=None, email=None, cedula=None):
		user = None
		if not id and not email and not cedula:
			return None
		try:
			if id:
				user = User.objects.get(id=int(id))
			elif email:
				user = User.objects.get(email=email)
			elif cedula:
				user = User.objects.get(cedula=cedula)
		except:
			pass
		return user

	def __get_user_json__(self, i):
		return {
			"first_name": i.user.first_name,
			"last_name": i.user.last_name,
			"email": i.user.email,
			"is_active": i.user.is_active,
			"is_admin": i.user.is_admin,
			"phone_number": i.user.phone_number,
			"cedula": i.user.cedula,
			"is_gas_station_admin": i.user.is_gas_station_admin,
			"city": i.user.city,
			"address": i.user.address,
			"balance": i.total,
			"id": i.user.pk,
			"vehicles_ids": self.__get_vehicles_ids(i.user),
		}


class PermissionService:

	ADD = "add"
	CHANGE = "change"
	DELETE = "delete"
	VIEW = "view"

	def create_permission_model(self, model: str, name: str, method: str):
		model_name = model.replace("_", "")
		content_type = ContentType.objects.get(model=model_name)

		Permission.objects.create(
			codename=f"can_{method}_{model}", name=name, content_type=content_type
		)

	def get_permissions_by_name(self, permissions_name: list):
		return [Permission.objects.get(name=name) for name in permissions_name]


def search_users(input_text):
	text = input_text.strip().lower()
	results = User.objects.raw(
		"""
		select 
			id, email, first_name, last_name, is_active
		from 
			users_user
		where 
			match(email, first_name, last_name) against(%s IN BOOLEAN MODE)
		LIMIT 4;
	""",
		[text + "*"],
	)

	return UserResultSerializer(results, many=True).data
