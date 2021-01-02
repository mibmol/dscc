from datetime import datetime, timedelta
from django.db import connection
from re import fullmatch
from purchase.models import Purchase, PurchaseFuelType
from company.models import CompanyAdminUser
from config.utils import get_env
import pytz

# from .serializers import TopUpSerializer
from django.utils import timezone
from .models import FuelType, Purchase, PurchaseRating
from .serializers import (
		GetPurchaseFuelTypeSerializer, 
		CreatedPurchaseSerializer, 
		PurchaseHistorySerializer,
		PurchaseDetailSerializer,
		PurchaseFuelTypeDetailSerializer, PurchaseRatingSerializer)
from .utils import generate_qr_code_string, generate_number_code
from company.models import GasStation, Company
from users.models import User, VehiclesId, UserGasStationBalance
from datetime import date, timedelta
from rest_framework.exceptions import APIException
from scripts.validate import validate_date_range, validate_num_range, validate_date_time_range
from users.models import UserStation
# from scripts.worker import ScheduleWorker, Task


class PurchaseService:
	def __wrap_purchase_fuel_type__(self, purchase):
		fuel = FuelType(name="No disponible", price_per_gallon=0)
		d = datetime.now()
		idp = int(f"{d.year}{d.month}{d.day}{d.second}")
		return PurchaseFuelType(id=idp, purchase=purchase, fuel_type=fuel)

	def __get_fuel_type__(self, purchases: list):
		is_done = []
		out = purchases.copy()
		for pur in out:
			if pur.is_done:
				is_done.append(pur)
				purchases.remove(pur)
		is_done = list(PurchaseFuelType.objects.filter(purchase__in=is_done))
		purchases = [self.__wrap_purchase_fuel_type__(purchase) for purchase in purchases]
		return purchases + is_done

	def get_purchase_company_filtered(
		self,
		user,
		from_date=None,
		to_date=None,
		min_amount=None,
		max_amount=None,
		gas_stations=[],
	):
		company = CompanyAdminUser.objects.get(user=user).company
		count_sts = len(gas_stations)
		if to_date:
			to_date = date.fromisoformat(to_date) + timedelta(days=1)
			to_date = to_date.isoformat()
		if from_date and to_date and max_amount and min_amount:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			if count_sts > 0:
				purchases = Purchase.objects.filter(
					company=company,
					created_at__range=[from_date, to_date],
					amount__gte=int(min_amount),
					amount__lte=int(max_amount),
					gas_station__id__in=gas_stations,
				)
			else:
				purchases = Purchase.objects.filter(
					company=company,
					created_at__range=[from_date, to_date],
					amount__gte=int(min_amount),
					amount__lte=int(max_amount),
				)
		elif from_date and to_date:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if count_sts > 0:
				purchases = Purchase.objects.filter(
					company=company,
					created_at__range=[from_date, to_date],
					gas_station__id__in=gas_stations,
				)
			else:
				purchases = Purchase.objects.filter(
					company=company, created_at__range=[from_date, to_date]
				)
		elif max_amount and min_amount:
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			if count_sts > 0:
				purchases = Purchase.objects.filter(
					company=company,
					amount__gte=int(min_amount),
					amount__lte=int(max_amount),
					gas_station__id__in=gas_stations,
				)
			else:
				purchases = Purchase.objects.filter(
					company=company, amount__gte=int(min_amount), amount__lte=int(max_amount),
				)
		elif count_sts > 0:
			purchases = Purchase.objects.filter(
				company=company, gas_station__id__in=gas_stations
			)
		else:
			purchases = Purchase.objects.filter(company=company)
		purchases = self.__get_fuel_type__(list(purchases))
		serializer = GetPurchaseFuelTypeSerializer(purchases, many=True)
		return serializer.data

	def get_purchase_fuel_type_company_filtered(
		self,
		user,
		from_date=None,
		to_date=None,
		min_amount=None,
		max_amount=None,
		gas_stations=[],
		fuel_types=[]
	):
		company = CompanyAdminUser.objects.get(user=user).company
		count_sts = len(gas_stations)
		count_ft = len(fuel_types)
		if to_date:
			to_date = date.fromisoformat(to_date) + timedelta(days=1)
			to_date = to_date.isoformat()
		if from_date and to_date and max_amount and min_amount:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			if count_sts > 0 and count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					purchase__gas_station__id__in=gas_stations,
					fuel_type__id__in=fuel_types
				)
			elif count_sts > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					purchase__gas_station__id__in=gas_stations,
				)
			elif count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					fuel_type__id__in=fuel_types
				)
			else:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
				)
		elif from_date and to_date:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if count_sts > 0 and count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					purchase__gas_station__id__in=gas_stations,
					fuel_type__id__in=fuel_types
				)
			elif count_sts > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					purchase__gas_station__id__in=gas_stations,
				)
			elif count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__created_at__range=[from_date, to_date],
					fuel_type__id__in=fuel_types
				)
			else:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company, 
					purchase__created_at__range=[from_date, to_date]
				)
		elif max_amount and min_amount:
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			if count_sts > 0 and count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					purchase__gas_station__id__in=gas_stations,
					fuel_type__id__in=fuel_types
				)
			elif count_sts > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					purchase__gas_station__id__in=gas_stations,
				)
			elif count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company,
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					fuel_type__id__in=fuel_types
				)
			else:
				purchases = PurchaseFuelType.objects.filter(
					purchase__company=company, 
					purchase__amount__gte=int(min_amount), 
					purchase__amount__lte=int(max_amount),
				)
		elif count_sts >0 and count_ft > 0:
			purchases = PurchaseFuelType.objects.filter(
				purchase__company=company, 
				purchase__gas_station__id__in=gas_stations,
				fuel_type__id__in=fuel_types
			)
		elif count_sts > 0:
			purchases = PurchaseFuelType.objects.filter(
				purchase__company=company, 
				purchase__gas_station__id__in=gas_stations
			)
		elif count_ft > 0:
			purchases = PurchaseFuelType.objects.filter(
				purchase__company=company, 
				fuel_type__id__in=fuel_types
			)
		else:
			purchases = PurchaseFuelType.objects.filter(company=company)
		serializer = GetPurchaseFuelTypeSerializer(purchases, many=True)
		return serializer.data

	def create(self, user, amount, gas_station, company, vehicle, balance_id):
		purchase = Purchase(
			user=user,
			amount=amount,
			company=Company(id=int(company.get("id"))),
			vehicle=VehiclesId(id=int(vehicle.get("id"))),
			gas_station=GasStation(id=int(gas_station.get("id"))),
		)
		balance = None
		balance_actual_total = None
		try:
			balance = UserGasStationBalance.objects.get(id=int(balance_id))
			balance_actual_total = balance.total
			if balance.total < amount:
				return False, {"msg": "Not enought credit"}
			balance.total = balance.total - amount
			balance.save()
		except Exception as e:
			print(e)
			return False, {"msg": "Error updating balance"}
		
		try:
			purchase.save()
			purchase.code_expiry_date = datetime.now(tz=timezone.utc) + timedelta(days=3)
			purchase.number_code = generate_number_code(purchase.id)
			purchase.qrcode_string = generate_qr_code_string(user, purchase)
			purchase.direct_buy_with_card = False
			purchase.save()
		except Exception as e:
			print(e)
			balance.total = balance_actual_total
			balance.save()
			return False, {"msg": "Error saving purchase"}

		return True, CreatedPurchaseSerializer(instance=purchase).data

	def make_purchase_done(self, purchase_id, fueltype_id, user):
		purchase = Purchase.objects.filter(id=int(purchase_id), user=user).first()
		if not purchase:
			return {'msg': 'bad purchase id'}, False
		fueltype = FuelType.objects.filter(id=int(fueltype_id)).first()
		if not fueltype:
			return {'msg': 'bad fueltype id'}, False
		
		purchase.is_done = True
		purchase.gallons = purchase.amount/fueltype.price_per_gallon

		try:
			pft = PurchaseFuelType(fuel_type=fueltype, purchase=purchase)
			pft.save()
		except Exception as e:
			return {'msg': "can't save the fueltype"}, False

		try:
			purchase.save()
		except Exception as e:
			return {'msg': "can't save the purchase"}, False
		
		return {'fueltype': fueltype, 'purchase': purchase}, True

	def get_last_puchases(self, user):
		company = CompanyAdminUser.objects.get(user=user).company
		to_date = datetime.now()
		from_date = to_date - timedelta(hours=48)

		purchases = Purchase.objects.filter(
			company=company, created_at__range=[from_date.isoformat(), to_date.isoformat()]
		)
		purchases = self.__get_fuel_type__(list(purchases))
		serializer = GetPurchaseFuelTypeSerializer(purchases, many=True)
		return serializer.data

	def get_last_puchases_gas_station(self, user):
		gas_station = UserStation.objects.get(user=user).gas_station
		to_date = datetime.now()
		from_date = to_date - timedelta(hours=48)

		purchases = Purchase.objects.filter(
			gas_station=gas_station,
			created_at__range=[from_date.isoformat(), to_date.isoformat()],
		)
		purchases = self.__get_fuel_type__(list(purchases))
		serializer = GetPurchaseFuelTypeSerializer(purchases, many=True)
		return serializer.data

	def get_purchase_gas_station_filtered(
		self, user, from_date=None, to_date=None, min_amount=None, max_amount=None,
	):
		gas_station = UserStation.objects.get(user=user).gas_station
		if to_date:
			to_date = date.fromisoformat(to_date) + timedelta(days=1)
			to_date = to_date.isoformat()

		if from_date and to_date and max_amount and min_amount:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")

			purchases = Purchase.objects.filter(
				gas_station=gas_station,
				created_at__range=[from_date, to_date],
				amount__gte=int(min_amount),
				amount__lte=int(max_amount),
			)
		elif from_date and to_date:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			purchases = Purchase.objects.filter(
				gas_station=gas_station, created_at__range=[from_date, to_date]
			)
		elif max_amount and min_amount:
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			purchases = Purchase.objects.filter(
				gas_station=gas_station,
				amount__gte=int(min_amount),
				amount__lte=int(max_amount),
			)
		else:
			purchases = Purchase.objects.filter(gas_station=gas_station)
		purchases = self.__get_fuel_type__(list(purchases))
		serializer = GetPurchaseFuelTypeSerializer(purchases, many=True)
		return serializer.data

	def get_purchase_fuel_type_gas_station_filtered(
			self, user, from_date=None, to_date=None, min_amount=None, max_amount=None, fuel_types=[]
		):
		gas_station = UserStation.objects.get(user=user).gas_station
		if to_date:
			to_date = date.fromisoformat(to_date) + timedelta(days=1)
			to_date = to_date.isoformat()
		count_ft = len(fuel_types)
		if from_date and to_date and max_amount and min_amount:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			
			if count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__gas_station=gas_station,
					purchase__created_at__range=[from_date, to_date],
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					fuel_type__id__in=fuel_types
				)
			else:
				purchases = PurchaseFuelType.objects.filter(
					purchase__gas_station=gas_station,
					purchase__created_at__range=[from_date, to_date],
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
				)
		elif from_date and to_date:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			if count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__gas_station=gas_station, 
					purchase__created_at__range=[from_date, to_date],
					fuel_type__id__in=fuel_types
				)
			else:
				purchases = PurchaseFuelType.objects.filter(
					purchase__gas_station=gas_station, 
					purchase__created_at__range=[from_date, to_date]
				)
		elif max_amount and min_amount:
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			if count_ft > 0:
				purchases = PurchaseFuelType.objects.filter(
					purchase__gas_station=gas_station,
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
					fuel_type__id__in=fuel_types
				)
			else:
				purchases = PurchaseFuelType.objects.filter(
					purchase__gas_station=gas_station,
					purchase__amount__gte=int(min_amount),
					purchase__amount__lte=int(max_amount),
				)
		else:
			purchases = PurchaseFuelType.objects.filter(purchase__gas_station=gas_station)
		serializer = GetPurchaseFuelTypeSerializer(purchases, many=True)
		return serializer.data

	def user_purchases(
		self, page:int, user:User, from_date=None, to_date=None, gas_station=None, limit=10):

		if page == None:
			raise APIException(detail="The page load is required")

		start = page * limit
		end = start + limit
		
		if not gas_station and from_date and to_date:
			if not validate_date_time_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			purchases = Purchase.objects.filter(
					user=user, 
					created_at__range=[from_date, to_date]
			).order_by("-created_at")[start:end]

		elif not gas_station and from_date:
			to_date = datetime.now().isoformat()
			if not validate_date_time_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			purchases = Purchase.objects.filter(
				user=user, 
				created_at__range=[from_date, to_date]
			).order_by("-created_at")[start:end]

		elif not gas_station and to_date:
			from_date = datetime(2020, 1, 1, 0, 0).isoformat()
			if not validate_date_time_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")
			purchases = Purchase.objects.filter(
				user=user, 
				created_at__range=[from_date, to_date]
			).order_by("-created_at")[start:end]

		elif gas_station != None: 
			try:
				purchases = Purchase.objects.filter(
					user=user, 
					gas_station__id=gas_station
				).order_by("-created_at")[start:end]

			except Exception as e:
				print(e)
				raise APIException(detail="La estación no existe")
		else:
			purchases = Purchase.objects.filter(user=user).order_by("-created_at")[start:end]

		serializer = PurchaseHistorySerializer(purchases, many=True)
		return serializer.data
		
	def purchase_by_id(self, user:User, id, is_done:bool):
		if is_done:
			try:
				purchasefueltype = PurchaseFuelType.objects.get(purchase__user=user, purchase__id=id)
				serializer = PurchaseFuelTypeDetailSerializer(purchasefueltype)
			except PurchaseFuelType.DoesNotExist:
				raise APIException(detail="Object with id don't exist")
		else:
			try:
				purchase = Purchase.objects.get(user=user, id=id)
				serializer = PurchaseDetailSerializer(purchase)
			except Purchase.DoesNotExist:
				raise APIException(detail="Object with id don't exist")
		
		return serializer.data
	
	def delete_purchase(self, user, id):
		utc = pytz.UTC
		try:
			purchase = Purchase.objects.get(user=user, id=id)
		except Purchase.DoesNotExist:
			raise APIException(detail="Object don't exist")
		expire = datetime.fromisoformat(purchase.code_expiry_date.isoformat())
		now = utc.localize(datetime.now())
		if purchase.is_done or expire < now:
			raise APIException(detail="Purchace can't be canceled")
		
		try:
			balance = UserGasStationBalance.objects.get(user=user, gas_station=purchase.gas_station)
		except UserGasStationBalance.DoesNotExist:
			raise APIException(detail="Balance don't exist")

		balance.total = balance.total + purchase.amount
		try:
			balance.save()
		except: 
			raise APIException(detail="Error save balance")
		
		try:
			purchase.delete()
		except: 
			balance.total = balance.total - purchase.amount
			balance.save()
			raise APIException(detail="Error cancel purchase")

		return {"status": 200}


class RatingService:
	def __init__(self):
		self.updating = False
		# self.schedule_worker = ScheduleWorker(loop_delay=4)
		# self.schedule_worker.start()
		self.run_updates()
	
	def run_updates(self):
		def runner():
			try:
				self.update_ratings()
			except Exception as e:
				print('from update:::', e)
				pass
		# self.schedule_worker.schedule(task=Task(runner), seconds=60, just_once=False)

	def rate_purchase(self, purchase_id: int, user: User, rating: int, comment=None):
		pr = PurchaseRating.objects.filter(purchase__id=purchase_id, user=user).first()
		if not pr:
			pr = PurchaseRating(purchase=Purchase(id=purchase_id), user=user)
		
		pr.rating = rating
		if comment:
			pr.comment = comment
		pr.save()
	
	def update_ratings(self):
		if self.updating:
			return
		self.updating = True
		with connection.cursor() as cursor:
			cursor.execute(self.build_update_query(avgs))
		self.updating = False

	def build_update_query(self, avgs):
		return f"""
			USE {get_env('DB_NAME')};
			UPDATE company_gasstation gs 
				INNER JOIN  (
					SELECT 
						p.gas_station_id as id,
						AVG(CAST(p_rating.rating as FLOAT)) as avg_rating
					FROM 
						purchase_purchaserating p_rating
						INNER JOIN purchase_purchase p
							ON p.id = p_rating.purchase_id
					GROUP BY 
						p.gas_station_id
					) averages
				ON averages.id = gs.id
			SET gs.global_purchase_rating = averages.avg_rating;

		"""
	def get_ratings_company_filtered(self, 
		user,
		from_date,
		to_date,
		gas_stations=[]
	):
		try:
			company = CompanyAdminUser.objects.get(user=user).company
		except CompanyAdminUser.DoesNotExist:
			raise APIException(detail="Internal server error")

		if to_date:
			to_date = date.fromisoformat(to_date) + timedelta(days=1)
			to_date = to_date.isoformat()

		count_sts = len(gas_stations)
		if from_date and to_date:
			if validate_date_range(from_date, to_date):
				if count_sts > 0:
					ratings = PurchaseRating.objects.filter(
						purchase__company=company,
						created_at__range=[from_date, to_date],
						purchase__gas_station__id__in=gas_stations
					)
				else:
					ratings = PurchaseRating.objects.filter(
						purchase__company=company,
						created_at__range=[from_date, to_date]
					)
			else:
				raise APIException(detail="Rango de fechas incorrecto")
		elif count_sts > 0:
			ratings = PurchaseRating.objects.filter(
					purchase__company=company,
					purchase__gas_station__id__in=gas_stations
				)
		else:
			ratings = PurchaseRating.objects.filter(
					purchase__company=company,
				)

		serializer = PurchaseRatingSerializer(ratings, many=True)
		return serializer.data

	def get_ratings_station_filtered(self, 
		user,
		from_date,
		to_date,
	):
		try:
			station = UserStation.objects.get(user=user).gas_station
		except CompanyAdminUser.DoesNotExist:
			raise APIException(detail="Internal server error")
		
		if to_date:
			to_date = date.fromisoformat(to_date) + timedelta(days=1)
			to_date = to_date.isoformat()

		if from_date and to_date:
			if validate_date_range(from_date, to_date):
					ratings = PurchaseRating.objects.filter(
						purchase__gas_station=station,
						created_at__range=[from_date, to_date],
					)
			else:
				raise APIException(detail="Rango de fechas incorrecto")
		else:
			ratings = PurchaseRating.objects.filter(
					purchase__gas_station=station,
				)

		serializer = PurchaseRatingSerializer(ratings, many=True)
		return serializer.data
