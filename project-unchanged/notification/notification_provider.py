from .notification_manager import NotificationManager, NotificationType
from company.models import Policies, TipAd
from purchase.models import PurchaseFuelType, FuelType, Purchase
from company.serializers import TipAdSerializer
from users.models import User
from topup.models import TopUpTransfer
from notification.models import Notification
from notification.serializers import NotificationSerializer
from django.db.models import Q

manager = NotificationManager()


def notificate_change_privacy_polices(polices: Policies):
	"""
		Notificate change privacy polices
	"""
	title = "Cambios de las políticas de la aplicación"
	body = "Abre la notificación para obtener más información"
	data = {
		"type": NotificationType.CHANGE_PRIVACY_POLICES,
		"polices": polices.description,
		"created_at": polices.modified_at.isoformat(),
	}

	try:
		Notification.objects.create(title=title, body=body, is_broadcast=True, data=data)
	except Exception as e:
		print(e)
		pass

	return manager.sendToAllUsers(title=title, body=body, data=data)


def notificate_purchase_complete(fuel_type: FuelType, purchase: Purchase):
	"""
		Notificate a purhcase is done
	"""
	title = "Compra completada"

	body = (
		"Se ha efectuado su compra por "
		+ str(purchase.amount)
		+ ", en la estación: "
		+ str(purchase.gas_station.name)
	)
	data = {
		"type": NotificationType.PURCHASE_DONE,
		"amount": str(purchase.amount),
		"purchase_id": str(purchase.id), 
		"fueltype": fuel_type.name,
		"gallons": str(purchase.gallons),
		"gas_station": purchase.gas_station.name,
		"created_at": purchase.created_at.isoformat(),
	}
	try: 
		Notification.objects.create(title=title, body=body, data=data, user=purchase.user)
	except Exception as e:
		print(e)
		pass
	return manager.sendToUser(user=purchase.user, title=title, body=body, data=data)


def notificate_tip_ad(tipAd: TipAd):
	"""
		Notificate tip or advertisement
	"""
	title = ""
	gas_station = None
	kind = ''
	if str(tipAd.kind) == 'TIP':
		kind = NotificationType.TIP
		if tipAd.gas_station != None:
			title = "Nuevo tip de " + "" + str(tipAd.gas_station.name)
			gas_station = tipAd.gas_station.name
		else:
			title = "Nuevo tip de " + "" + str(tipAd.company.trade_name)
	elif str(tipAd.kind) == 'AD':
		kind = NotificationType.ADVERTISEMENT
		if tipAd.gas_station != None:
			title = "Nuevo anuncio de " + str(tipAd.gas_station.name)
			gas_station = tipAd.gas_station.name
		else:
			title = "Nuevo anuncio de " + str(tipAd.company.trade_name)

	body = tipAd.title

	serializer = TipAdSerializer(tipAd)
	data = {
		"type": kind,
		"gas_station": str(gas_station),
		"company": tipAd.company.trade_name,
	}
	contenedor = serializer.data
	contenedor['id'] = str(contenedor['id'])
	data.update(contenedor)
	try:
		Notification.objects.create(title=title, body=body, data=data, is_broadcast=True)
	except Exception as e:
		print(e)
		pass

	return manager.sendToAllUsers(title=title, body=body, data=data, image=tipAd.img_path)


def notificate_enable_disable_service(user: User, status:bool):
	"""
		Notificate when a user is disabled or enabled
	"""
	if not status:
		title = "Bloqueo de usuario"
		body = "Su cuenta ha sido bloqueada indefinidamente por icumplir con nuestras plíticas"
		data = {"type": NotificationType.DISABLE_USER}
	else:
		title = "Usuario habilitado"
		body = "Su cuenta ha sido restablecida"
		data = {"type": NotificationType.ENABLE_USER}

	return manager.sendToUser(user=user, title=title, body=body, data=data)


def notificate_transfer(transfer: TopUpTransfer):
	"""
		Notificate when doing a transfer
	"""
	sender = transfer.sender_user
	receiver = transfer.receiver_user
	name = str(sender.first_name) + " " + (sender.last_name)
	amount = transfer.amount
	gas_station = transfer.gas_station.name
	title = f"{name} le ha transferido saldo"
	body = f"Se le acreditado ${amount}, que puede ser usado en la estación: {gas_station}"
	data = {
		"type": NotificationType.TRANSFER,
		"sender": name,
		"created_at": transfer.created_at.isoformat(),
		"amount": f"{amount}",
		"gas_station": gas_station,
		"company": transfer.company.trade_name,
	}

	try:
		Notification.objects.create(title=title, body=body, data=data, user=receiver)
	except:
		pass
	return manager.sendToUser(receiver, title=title, body=body, data=data)


def token_in_devices(token: str, devices: list):
	for device in devices:
		if device.get("token", "x").strip() == token.strip():
			return True
	return False


def register_user_device_token(user: User, device: dict):
	if device:
		token = device.get("token")
		devices = user.devices
		if not devices:
			devices = list()

		if token and not token_in_devices(token, devices):
			devices.append(device)
			user.devices = devices
			user.save()


def delete_user_device_token(user: User, token: str):
	if token and user.devices:
		devices = user.devices
		if not devices:
			return True
		for device in devices:
			if device.get("token") == token:
				user.devices.remove(device)
				user.save()
				return True
	return False


def get_notifications_new(user: User):
	ns = Notification.objects.filter(Q(user=user) | Q(is_broadcast=True)).order_by("-id")[:8]
	return NotificationSerializer(ns, many=True).data


def get_notifications_old(user: User, last_id: int):
	ns = Notification.objects.filter(
		(Q(user=user) | Q(is_broadcast=True)) & Q(id__lt=last_id)
	).order_by("-id")[:12]
	return NotificationSerializer(ns, many=True).data
