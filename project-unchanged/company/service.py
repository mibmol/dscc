from purchase.serializers import GetFuelTypeSerializer
from .models import Company, CompanyAdminUser, GasStation, TipAd, UserTipAdLike, Policies
from users.models import UserStation, User
from purchase.models import FuelType
from .serializers import (
	BasicGasStationSerializer,
	CompanyBasicSerializer,
	GasStationSerializer,
	GasStationNestedSerializer,
	PoliciesSerializer,
	CreateTipAdSerializer,
	CoordSerializer,
	TipAdSerializer,
	TipAdSerializerAll,
)
from users.serializers import (
	CompleteTipAdSerializer,
	BasicTipAdSerializer,
	UserStationSerializer,
)
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_401_UNAUTHORIZED
from notification.notification_provider import (
	notificate_change_privacy_polices,
	notificate_tip_ad,
)
from datetime import datetime
from .utils import submit_image
from math import e, sqrt


class CompanyService:
	def get_station(self, station_id: int):
		if not station_id:
			return None
		try:
			result = GasStation.objects.prefetch_related("company").get(id=station_id)
		except:
			result = None

		if not result:
			return None

		return GasStationNestedSerializer(result).data

	def __get_json__(self, i):
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
			"role": i.user.groups.all()[0].name,
			"id": i.user.pk,
		}

	def get_company_users(self, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			return []
		compadmins = CompanyAdminUser.objects.filter(company=company)
		admins_c = [self.__get_json__(i) for i in compadmins]
		stations = GasStation.objects.filter(company=company)
		usrStationa = UserStation.objects.filter(gas_station__in=stations)

		admins_s = []
		for i in usrStationa:
			data = self.__get_json__(i)
			data["gas_station"] = i.gas_station.name
			admins_s.append(data)

		response = admins_c + admins_s

		return sorted(response, key=lambda i: i["id"])

	def __gas_station_in_users__(self, gas_id, users):
		out = []
		for user in users:
			if user["gas_station"] == gas_id:
				out.append(user["user"])
		return out

	def get_company_stations(self, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			return []
		gas_stations = GasStation.objects.filter(company=company)
		serializer = GasStationSerializer(gas_stations, many=True)
		return serializer.data

	def get_company_stations_detail(self, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			return []
		gas_stations = GasStation.objects.filter(company=company)
		users = UserStation.objects.filter(gas_station__in=gas_stations)
		users = UserStationSerializer(users, many=True).data
		serializer = GasStationSerializer(gas_stations, many=True)
		data = serializer.data
		out = []
		for i in data:
			results = self.__gas_station_in_users__(i["id"], users)
			i["users"] = results
			out.append(i)
		return out

	def put_gas_station(self, data):
		serializer = GasStationSerializer(data=data)
		try:
			gas_station = GasStation.objects.get(id=data["id"])
			data["company"] = gas_station.company.id
		except GasStation.DoesNotExist:
			raise APIException(detail="gas station don't exist.")

		if serializer.is_valid(raise_exception=True):
			serializer.update(gas_station, serializer.validated_data)
			return serializer.data

	def create_gas_station(self, data, user):
		serializer = GasStationSerializer(data=data)
		try:
			company = CompanyAdminUser.objects.get(user=user).company
			data["company"] = company.id
		except CompanyAdminUser.DoesNotExist:
			raise APIException(detail="company don't exist.")

		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return serializer.data

	def delete_gas_station(self, id):
		try:
			GasStation.objects.get(id=id).delete()
		except GasStation.DoesNotExist:
			raise APIException(detail="gas station don't exist.")
		return {"status": 200}

	def get_gas_station_tipads(self, user):
		try:
			gas_station = UserStation.objects.get(user=user).gas_station
		except UserStation.DoesNotExist:
			return []
		tiaps = TipAd.objects.filter(gas_station=gas_station).order_by("-created_at")
		serializer = BasicTipAdSerializer(tiaps, many=True)
		return serializer.data

	def get_company_tipads(self, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			return []
		tiaps = TipAd.objects.filter(company=company).order_by("-created_at")
		serializer = BasicTipAdSerializer(tiaps, many=True)
		return serializer.data

	def get_compay_polices(self, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			try:
				company = UserStation.objects.get(user=user).gas_station.company
			except UserStation.DoesNotExist:
				return {}

		try:
			policies = Policies.objects.get(company=company)
		except Policies.DoesNotExist:
			return {}

		serializer = PoliciesSerializer(policies)
		return serializer.data

	def create_company_policies(self, user, description):
		if description == None or description == "":
			raise APIException(detail="Description is empty or null.")
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			raise APIException(detail="User don't match with any company")

		try:
			policies = Policies.objects.get(company=company)
			raise APIException(detail="Policies already exist")
		except Policies.DoesNotExist:
			policies = Policies(description=description, company=company)
			policies.save()
			notificate_change_privacy_polices(policies)
			return {"status": 200}

	def update_company_policies(self, user, id, description):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			raise APIException(detail="User don't match with any company")
		try:
			policies = Policies.objects.get(id=id)
			policies.description = description
			policies.modified_at = datetime.now()
			policies.save()
			notificate_change_privacy_polices(policies)
			return {"status": 200}
		except Policies.DoesNotExist:
			raise APIException(detail="Policie don't exist")

	def get_companies(self):
		companies = Company.objects.all()
		serializer = CompanyBasicSerializer(companies, many=True)
		return serializer.data

	def get_gas_stations_company(self, id):
		gas_stations = GasStation.objects.filter(company__id=id)
		serializer = BasicGasStationSerializer(gas_stations, many=True)
		return serializer.data

	def get_fuel_types(self, user: User):
		if user.is_admin:
			try:
				company = CompanyAdminUser.objects.get(user=user).company
			except CompanyAdminUser.DoesNotExist:
				raise APIException(detail="Company dont exist")
		elif user.is_gas_station_admin:
			try:
				company = UserStation.objects.get(user=user).gas_station.company
			except:
				raise APIException(detail="Gas station dont exist")
		else:
			raise APIException(detail="User dont authorize")

		fuel = FuelType.objects.filter(company=company)
		serializer = GetFuelTypeSerializer(fuel, many=True)
		return serializer.data


class TipAdService:
	def create(self, user, data, image_file):
		data._mutable = True
		try:
			gas_station = UserStation.objects.get(user=user).gas_station
			company = gas_station.company.id
			gas_station = gas_station.id
		except UserStation.DoesNotExist:
			company = CompanyAdminUser.objects.get(user=user).company.id
			gas_station = None
		data.pop("image", None)
		if image_file == None:
			raise APIException(detail="Image is required")
		if image_file.name.split(".")[-1] not in ["jpg", "jpeg", "png", "gif"]:
			raise APIException(detail="Only accpet images files: jpg, jpeg, png, gif")
		if image_file.size > (10 * 1024 * 1024):
			raise APIException(detail="Maximum image size: 10 MB")
		data["created_by"] = user.id
		data["company"] = company
		data["gas_station"] = gas_station
		data["img_path"] = submit_image(image_file)
		serialized = CreateTipAdSerializer(data=data)
		if serialized.is_valid(raise_exception=True):
			created_tipad = serialized.save()
			notificate_tip_ad(created_tipad)
		return {"status": 200}

	def get_tipad_company(self, id, user):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			return {}
		try:
			tiaps = TipAd.objects.get(id=id, company=company)
		except TipAd.DoesNotExist:
			raise APIException(detail="Usuario no autorizado", code=HTTP_401_UNAUTHORIZED)
		serializer = CompleteTipAdSerializer(tiaps)
		return serializer.data

	def get_tipad_gas_station(self, id, user):
		try:
			gas_station = UserStation.objects.get(user=user).gas_station
		except UserStation.DoesNotExist:
			return {}
		try:
			tiaps = TipAd.objects.get(id=id, gas_station=gas_station)
		except TipAd.DoesNotExist:
			raise APIException(detail="Usuario no autorizado", code=HTTP_401_UNAUTHORIZED)
		serializer = CompleteTipAdSerializer(tiaps)
		return serializer.data

	def get_tips_app(self, limit=6):
		results = (
			TipAd.objects.prefetch_related("company")
			.filter(kind="tip")
			.order_by("-id")[:limit]
		)
		return TipAdSerializerAll(results, many=True).data
	
	def get_ads_app(self, limit=6):
		results = TipAd.objects.filter(kind="AD").order_by("-id")[:limit]
		return TipAdSerializer(results, many=True).data

	def get_tips_app_old(self, last_id, limit=8):
		results = (
			TipAd.objects.prefetch_related("company")
			.filter(kind="tip", id__lt=last_id)
			.order_by("-id")[:limit]
		)
		return TipAdSerializerAll(results, many=True).data

	def get_liked_tips(self, user, start_id, end_id):
		results = UserTipAdLike.objects.filter(
			user=user, tipad_id__gt=start_id, tipad_id__lt=end_id, is_like=True
		)
		return [usertip.tipad.id for usertip in results]

	def like_tipad(self, tipadid, user):
		tipad = TipAd.objects.get(id=tipadid)
		created_new = False
		user_tipad = UserTipAdLike.objects.filter(user=user, tipad=tipad).first()
		if not user_tipad:
			user_tipad = UserTipAdLike(tipad=tipad, user=user)
			created_new = True

		if created_new:
			tipad.like_count += 1
		else:
			if not user_tipad.is_like:
				tipad.like_count += 1
		user_tipad.is_like = True
		user_tipad.save()
		tipad.save()

	def dislike_tipad(self, tipadid, user):
		tipad = TipAd.objects.get(id=tipadid)
		created_new = False
		user_tipad = UserTipAdLike.objects.filter(user=user, tipad=tipad).first()
		if not user_tipad:
			user_tipad = UserTipAdLike(tipad=tipad, user=user)
			created_new = True

		if not created_new:
			if user_tipad.is_like and tipad.like_count > 0:
				tipad.like_count -= 1
		user_tipad.is_like = False
		user_tipad.save()
		tipad.save()


def search_stations(text="", limit=4):
	stations = GasStation.objects.raw(
		"""
		select 
			*
		from 
			company_gasstation
		where 
			match(name, address) against(%s IN BOOLEAN MODE)
		LIMIT %s;
	""",
		[text.lower() + "*", limit],
	)

	return GasStationSerializer(stations, many=True).data


DEFAULT_COORD_LAT = -2.171499
DEFAULT_COORD_LNG = -79.891971


def search_near_to(coord, limit=7):
	serializer = CoordSerializer(data=coord)
	if not serializer.is_valid():
		return []
	lat = coord.get("latitude", DEFAULT_COORD_LAT)
	lng = coord.get("longitude", DEFAULT_COORD_LNG)

	stations = GasStation.objects.all()
	serializer = GasStationSerializer(stations, many=True)
	with_distances = []
	for station in serializer.data:
		_lat = station.get("latitude")
		_lng = station.get("longitude")
		d = sqrt((_lat - lat) ** 2 + (_lng - lng) ** 2)
		with_distances.append({"station": station, "distance": d})
	with_distances.sort(key=lambda e: e["distance"])
	with_distances = with_distances[:limit]
	return [wd.get("station") for wd in with_distances]

