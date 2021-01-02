## business logic quering
## All data manipulation should be done here
## avoid doing it on django views
from rest_framework.exceptions import APIException, ValidationError
from .serializers import (
	CreateUserSerializer,
	CreateUserAdminSerializer,
	GetUserGasStationBalance, ReportUserGasStationBalance,
)
from .models import User, VehiclesId, UserGasStationBalance, UserStation
from .serializers import (
	GetUserSerializer,
	GetBillingDataSerializer,
	UpdateBillingDataSerializer,
	UpdateUserSerializer,
	VehiclesIdSerializer,
	UserResultSerializer,
	BalanceSerializer,
)

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import exceptions, serializers
from company.models import CompanyAdminUser, GasStation, Company
from django.contrib.auth.models import Group
from purchase.models import Purchase
from .utils.utils import remove_key_from_list

from notification.notification_provider import notificate_enable_disable_service

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
		self.role_service = RoleService()

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

	def create_user(self, data):
		created_user = None
		data["has_provided_password"] = data.get("has_provided_password", True)
		serialized = CreateUserSerializer(data=data)
		if serialized.is_valid(raise_exception=True):
			created_user = serialized.save()
		return created_user

	def create_user_admin(self, data, admin):
		created_user = None
		role = data.pop("role", None)
		data["has_provided_password"] = True
		data["is_admin"] = role == "CompanyAdministrators"
		data["is_gas_station_admin"] = role == "StationAdministrators"
		sid = data.pop("gas_station", 1)
		serialized = CreateUserAdminSerializer(data=data)
		if serialized.is_valid(raise_exception=True):
			created_user = serialized.save()
			self.role_service.assign_role(role, created_user, admin, sid)
		return created_user

	def create_user_balances(self, user):
		stations = GasStation.objects.all()[:2]
		balances = [
			UserGasStationBalance(user=user, gas_station=station, company=station.company)
			for station in stations
		]
		UserGasStationBalance.objects.bulk_create(balances)

	def update_user_data(self, data):
		user = User.objects.get(email=data["email"])
		full_user = User.objects.prefetch_related("vehicles_ids").get(id=user.id)
		serializer = UpdateUserSerializer(full_user, data=data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			full_user.vehicles_ids.all().delete()
			new_vehicles = data.get("vehicles_ids", [])
			if len(new_vehicles) > 0:
				VehiclesId.objects.bulk_create(
					[VehiclesId(**v, user=user) for v in new_vehicles]
				)
		return serializer.data

	def get_billing_data(self, user):
		full_user = User.objects.get(id=user.id)
		result = GetBillingDataSerializer(full_user).data
		result["vehicles_ids"] = [
			v for v in result.get("vehicles_ids", []) if not v.get("deleted")
		]
		return result

	def update_billing_data(self, user, data):
		full_user = User.objects.get(id=user.id)
		serializer = UpdateBillingDataSerializer(full_user, data=data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			VehiclesId.objects.filter(user=user).update(deleted=True)
			new_vehicles = data.get("vehicles_ids", [])
			new_vehicles = remove_key_from_list("id", new_vehicles)
			if len(new_vehicles) > 0:
				ids = [VehiclesId(**v, user=user) for v in new_vehicles]
				created = VehiclesId.objects.bulk_create(ids)
		return serializer.data

	def get_vehicles(self, user):
		result = VehiclesId.objects.filter(user=user, deleted=False)
		serializer = VehiclesIdSerializer(result, many=True)
		return serializer.data

	def get_balance(self, user, station_id=None):
		balance = None
		try:
			balance = UserGasStationBalance.objects.get(
				user=user, gas_station=GasStation(id=station_id)
			)
		except:
			return None

		return BalanceSerializer(balance).data

	def get_company_balances(self, user):
		balances = (
			UserGasStationBalance.objects.filter(user=user)
			.prefetch_related("company")
			.prefetch_related("gas_station")
		)

		serializer = GetUserGasStationBalance(balances, many=True)
		return serializer.data

	def __get_vehicles_ids(self, user):
		vehicles_ids = VehiclesId.objects.filter(user=user, deleted=False)
		return VehiclesIdSerializer(vehicles_ids, many=True).data

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

	def get_users_by_company(self, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
			balances = UserGasStationBalance.objects.filter(company=company).order_by(
				"user__pk"
			)
			# print("balances:::", list(balances))
		except CompanyAdminUser.DoesNotExist:
			return []
		except UserGasStationBalance.DoesNotExist:
			return []
		res = [self.__get_user_json__(i) for i in balances]
		return dict((v["id"], v) for v in res).values()
	
	def get_users_by_compnay_filtered(self, 
		user,  
		is_active,
		gas_stations=[]):

		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			return []
		count_sts = len(gas_stations)
		
		if is_active != None:
			if count_sts > 0:
				balances = UserGasStationBalance.objects.filter(
					company=company,
					user__is_active=is_active,
					gas_station__in=gas_stations
				).order_by("user__pk")
			else:
				balances = UserGasStationBalance.objects.filter(
					company=company,
					user__is_active=is_active
				).order_by("user__pk")
		elif count_sts > 0:
			balances = UserGasStationBalance.objects.filter(
				company=company,
				gas_station__in=gas_stations
			).order_by("user__pk")
		else:
			balances = UserGasStationBalance.objects.filter(
				company=company
			).order_by("user__pk")

		serializer = ReportUserGasStationBalance(balances, many=True)
		return serializer.data

	def get_users_by_station_filtered(self, 
		user,
		is_active):
		try:
			station = UserStation.objects.get(user=user).gas_station
		except UserStation.DoesNotExist:
			return []
		
		if is_active != None:
			balances = UserGasStationBalance.objects.filter(
				gas_station=station,
				user__is_active=is_active,
			).order_by("user__pk")
		else:
			balances = UserGasStationBalance.objects.filter(
				gas_station=station
			).order_by("user__pk")
		
		serializer = ReportUserGasStationBalance(balances, many=True)
		return serializer.data

	def get_users_by_station(self, user):
		try:
			station = UserStation.objects.get(user=user).gas_station
			balances = UserGasStationBalance.objects.filter(gas_station=station).order_by(
				"user__pk"
			)
		except UserStation.DoesNotExist:
			return []
		except UserGasStationBalance.DoesNotExist:
			return []
		res = [self.__get_user_json__(i) for i in balances]
		return dict((v["id"], v) for v in res).values()

	def get_balance_by_id(self, balance_id):
		balance = None
		try:
			balance = (
				UserGasStationBalance.objects.prefetch_related("company")
				.prefetch_related("gas_station")
				.get(id=int(balance_id))
			)
		except:
			pass
		return balance

	def change_status(self, email, new_status):
		"""
		Change status to user (active, inactive)
		"""
		if new_status == None:
			raise ValidationError(detail="field new_status is required")

		if not email:
			raise ValidationError(detail="field email is required")

		try:
			user = User.objects.get(email=email)
		except:
			raise ValidationError(detail="User don't exist")

		user.is_active = new_status
		try:
			user.save()
		except:
			raise APIException(detail="Error ocurrido al intentar cambiar el estado del usuario")
		notificate_enable_disable_service(user, new_status)
		return {"status": 200}


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


class RoleService:
	def __init__(self):
		self.service = PermissionService()

	def create_role(self, name: str, permissions):
		new_group, created = Group.objects.get_or_create(name=name)
		new_group.permissions.set(permissions)
		return new_group

	def assign_role(self, role: str, user, admin, station_id):
		"""
			Method allowed assign for a user.
		"""
		try:
			group = Group.objects.get(name=role)
			self.toggle_model(user, admin, role, station_id)
			group.user_set.add(user)
			return group
		except:
			raise exceptions.APIException(f"Role {role} don't exist.")

	def get_all_roles(self):
		roles = list(Group.objects.all())
		return [
			{"name": role.name, "permissions": [perm.name for perm in role.permissions.all()],}
			for role in roles
		]

	def get_role_by_name(self, name: str):
		group, created = Group.objects.get_or_create(name=name)
		return group

	def change_user_role(self, email: str, role_name: str, admin, station=None):
		"""
			Method allowed change for a user.
		"""
		user = User.objects.get(email=email)
		not_same_admin = user.is_admin and role_name == "StationAdministrators"
		not_same_adsts = user.is_gas_station_admin and role_name == "CompanyAdministrators"
		if not_same_admin or not_same_adsts:
			try:
				user.groups.all()[0].user_set.remove(user)
			except:
				pass
			return self.assign_role(role_name, user, admin, station)

	def toggle_model(self, user, admin, role: str, station):
		"""
			Model manager for roles. 
			If you need add more roles, only edit this method
		"""
		if role == "CompanyAdministrators":
			company = CompanyAdminUser.objects.get(user=admin).company
			CompanyAdminUser(user=user, company=company).save()
			user.is_admin = True
			user.is_gas_station_admin = False
			user.save()
			try:
				UserStation.objects.get(user=user).delete()
			except:
				pass

		elif role == "StationAdministrators":
			if station != None:
				gas_station = GasStation.objects.get(pk=station)
				UserStation(user=user, gas_station=gas_station).save()
				user.is_admin = False
				user.is_gas_station_admin = True
				user.save()
			else:
				raise exceptions.APIException("Don't provieder gas station")
			try:
				CompanyAdminUser.objects.get(user=user).delete()
			except:
				pass


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

class ResetPassword:
	def send_email(self, user):
		uid = urlsafe_base64_encode(force_bytes(user.id))
		
		token = self.generate_token(user)
		link = reverse('reset-user-password', kwargs={'uidb64': uid, 'token': token})
		reset_url = HOST_ACTUAL+link
		
		message_email = "<p>Estimado "+ user.first_name +' '+ user.last_name +",</p><p>Para iniciar el proceso de restablecimiento de contraseña, haga clic en el siguiente enlace: <br>" + reset_url +"</p><p>Si al hacer clic en el enlace no funciona, copie y pegue el URL en un navegador.</p><br><p>Saludos,<br>El equipo de Pagos a Gasolineras.</p>" 
		
		payload = json.dumps({
			"to": user.email,
			"subject": 'Recuperar contraseña Pagos a Gasolineras',
			"html": message_email,
			"sendername": "Pagos a Gasolineras"
		})

		headers = {
			'content-type' : "application/json",
			'x-apikey' : RESTDB_API_KEY,
			'cache-control' : 'no-cache'
		}
		
		response = requests.request("POST", RESTDB_MAIL_HOST, data=payload, headers=headers)
		
	def generate_token(self, user):
		payloadT = {
			'id': user.id, 
			'email': user.email, 
			'first_name': user.first_name, 
			'last_name': user.last_name,
			'exp': datetime.utcnow() + timedelta(seconds=int(JWT_EXP_DELTA_SECONDS))
		}
		jwt_token = jwt.encode(payloadT, JWT_SECRET, algorithm=JWT_ALGORITHM)
		return jwt_token.decode('utf-8')

	def verify_token(self, jwt_token):
		try:
			payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
		except (jwt.DecodeError, jwt.ExpiredSignatureError):
			return None
		return payload

	def verify_user_token_uidb(self, payload, user):
		return payload['id'] == user.id and payload['first_name'] == user.first_name and payload['last_name'] == user.last_name and payload['email'] == user.email
