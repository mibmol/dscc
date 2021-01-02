###################################################################################
# This file is only use to test notifications, don´t use in production

from config.settings import DATABASES
from users.permissions import IsCompanyAdmin

from rest_framework import exceptions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import notification.notification_provider as provider
from company.models import Policies, Company, GasStation, TipAd
from users.models import User
from purchase.models import Purchase, FuelType, PurchaseFuelType
from datetime import datetime
from topup.models import TopUpTransfer
#from scripts.worker import Task, queue_worker


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def notificate(request):
	company = Company.objects.get(ruc="1234500000")
	polices = Policies(
		company=company,
		description="Nuevas politicas",
		created_at=datetime.now(),
		modified_at=datetime.now(),
	)
	try:
		provider.notificate_change_privacy_polices(polices)
	except:
		pass

	# queue_worker.add_task(Task(runner))
	return Response(data={"done": "yep"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def notificate2(request):
	def runner():
		company = Company.objects.get(ruc="1234500000")
		fuel = FuelType(name="super", price_per_gallon=10)
		# user = User.objects.get(cedula="0952770387")
		user = User.objects.get(id=1)
		gas = GasStation(
			ruc="1234510000",
			address="direccion",
			company=company,
			name="test",
			is_pilot=True,
			latitude=0.1,
			longitude=-0.78,
		)
		purchase = Purchase(
			created_at=datetime.now(), amount=5, gallons=2, user=user, gas_station=gas
		)
		provider.notificate_purchase_complete(fuel_type=fuel, purchase=purchase)

	try:
		runner()
	except:
		pass
	# queue_worker.add_task(Task(runner))
	return Response(data={"done": "yep"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def notificate3(request):
	def runner():
		company = Company.objects.get(ruc="1234500000")
		gas = GasStation(
			ruc="1234510000",
			address="direccion",
			company=company,
			name="test",
			is_pilot=True,
			latitude=0.1,
			longitude=-0.78,
		)
		tipAd = TipAd(
			kind="TIP",
			created_at=datetime.now(),
			title="Title",
			description="Descripcion",
			img_path="https://i.imgur.com/t0rP389.jpg",
			gas_station=gas,
			company=company,
		)
		provider.notificate_tip_ad(tipAd)
	try:
		runner()
	except:
		pass
	# queue_worker.add_task(Task(runner))
	return Response(data={"done": "yep"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def notificate4(request):
	user = User.objects.get(cedula="0952770387")
	res = provider.notificate_disable_service(user)
	return Response(data=res)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def notificate5(request):
	def runner():
		sender = User.objects.get(email="jperez@outlook.com")
		receiver = User.objects.get(email="super@email.com")
		gas = GasStation.objects.get(ruc="4444444444")
		transfer = TopUpTransfer(
			amount=15.0,
			created_at=datetime.now(),
			receiver_user=receiver,
			sender_user=sender,
			company=gas.company,
			gas_station=gas,
		)
		provider.notificate_transfer(transfer)

	try:
		runner()
	except:
		pass
	# queue_worker.add_task(Task(runner))
	return Response(data={"done": "yep"})
