from topup.models import TopUp, TopUpTransfer
from company.models import CompanyAdminUser
from users.models import UserStation, UserGasStationBalance, User
from .serializers import TopUpSerializer, TransferSerializer
from datetime import date
from rest_framework.exceptions import APIException
from scripts.validate import validate_date_range, validate_num_range
from datetime import datetime, timedelta
from django.db.models import Q
from notification.notification_provider import notificate_transfer

class TopupService:
	def create_topup(self, user, company, amount):
		return TopUp.objects.create(user=user, company=company, amount=amount)

	def get_topup_company_filtered(
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
				topups = TopUp.objects.filter(
					company=company,
					created_at__range=[from_date, to_date],
					amount__gte=int(min_amount),
					amount__lte=int(max_amount),
					gas_station__id__in=gas_stations,
				)
			else:
				topups = TopUp.objects.filter(
					company=company,
					created_at__range=[from_date, to_date],
					amount__gte=int(min_amount),
					amount__lte=int(max_amount),
				)

		elif from_date and to_date:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")

			if count_sts > 0:
				topups = TopUp.objects.filter(
					company=company,
					created_at__range=[from_date, to_date],
					gas_station__id__in=gas_stations,
				)
			else:
				topups = TopUp.objects.filter(
					company=company, created_at__range=[from_date, to_date]
				)

		elif max_amount and min_amount:
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			if count_sts > 0:
				topups = TopUp.objects.filter(
					company=company,
					amount__gte=int(min_amount),
					amount__lte=int(max_amount),
					gas_station__id__in=gas_stations,
				)
			else:
				topups = TopUp.objects.filter(
					company=company, amount__gte=int(min_amount), amount__lte=int(max_amount)
				)
		elif count_sts > 0:
			topups = TopUp.objects.filter(company=company, gas_station__id__in=gas_stations)
		else:
			topups = TopUp.objects.filter(company=company)

		serializer = TopUpSerializer(topups, many=True)
		return serializer.data

	def get_last_topups(self, user):
		company = CompanyAdminUser.objects.get(user=user).company
		to_date = datetime.now()
		from_date = to_date - timedelta(hours=48)
		topups = TopUp.objects.filter(
			company=company, created_at__range=[from_date.isoformat(), to_date.isoformat()]
		)
		serializer = TopUpSerializer(topups, many=True)
		return serializer.data

	def get_last_topups_gas_station(self, user):
		gas_station = UserStation.objects.get(user=user).gas_station
		to_date = datetime.now()
		from_date = to_date - timedelta(hours=48)
		topups = TopUp.objects.filter(
			gas_station=gas_station,
			created_at__range=[from_date.isoformat(), to_date.isoformat()],
		)
		serializer = TopUpSerializer(topups, many=True)
		return serializer.data

	def get_topup_gas_station_filtered(
		self, user, from_date=None, to_date=None, min_amount=None, max_amount=None
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

			topups = TopUp.objects.filter(
				gas_station=gas_station,
				created_at__range=[from_date, to_date],
				amount__gte=int(min_amount),
				amount__lte=int(max_amount),
			)

		elif from_date and to_date:
			if not validate_date_range(from_date, to_date):
				raise APIException("Rango de fechas incorecto")

			topups = TopUp.objects.filter(
				gas_station=gas_station, created_at__range=[from_date, to_date]
			)

		elif max_amount and min_amount:
			if not validate_num_range(min_amount, max_amount):
				raise APIException("Rango de montos incorecto")
			topups = TopUp.objects.filter(
				gas_station=gas_station,
				amount__gte=int(min_amount),
				amount__lte=int(max_amount),
			)
		else:
			topups = TopUp.objects.filter(gas_station=gas_station)

		serializer = TopUpSerializer(topups, many=True)
		return serializer.data


class TransferService:
	def get_by_id(self, transfer_id):
		transfer = None
		try:
			transfer = (
				UserGasStationBalance.objects.prefetch_related("gas_station")
				.prefetch_related("receiver_user")
				.prefetch_related("sender_user")
				.get(id=int(transfer_id))
			)
			return TransferSerializer(transfer).data
		except Exception as e:
			print(e)
		return transfer

	def get_all_by_user(self, user):
		user_balance = UserGasStationBalance(user=user)
		transfers = (
			TopUpTransfer.objects.prefetch_related("gas_station")
			.prefetch_related("receiver_user")
			.prefetch_related("sender_user")
			.filter(Q(sender_user=user) | Q(receiver_user=user))
		)

		return TransferSerializer(transfers, many=True).data

	def create_transfer(self, receiver_user, sender_user, balance, amount):
		if balance.total < amount:
			return False, {"msg", "No enought credit"}
		transfer = TopUpTransfer(
			receiver_user=receiver_user,
			sender_user=sender_user,
			amount=amount,
			user_balance=balance,
			company=balance.company,
			gas_station=balance.gas_station,
		)
		try:
			transfer.save()
		except:
			return False, {"msg": "can't save the transaction"}
			
		actual_total = balance.total
		try:
			balance.total = actual_total - amount
			balance.save()
		except:
			balance.total = actual_total
			balance.save()
			transfer.delete()
			return False, {"msg": "can't update the models"}

		receiver_balance = None
		try:
			receiver_balance = UserGasStationBalance.objects.get(
				user=receiver_user, gas_station=balance.gas_station
			)
			receiver_balance.total = receiver_balance.total + amount
			receiver_balance.save()
		except UserGasStationBalance.DoesNotExist:
			receiver_balance = UserGasStationBalance(
				user=receiver_user, gas_station=balance.gas_station, company=balance.company
			)
			receiver_balance.total = amount
			receiver_balance.save()

		notificate_transfer(transfer)
		return True, TransferSerializer(transfer).data

