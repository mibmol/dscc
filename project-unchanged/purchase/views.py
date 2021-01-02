from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from .service import PurchaseService, RatingService
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.permissions import IsGasStationAdmin, IsSuperUser, IsCompanyAdmin
from users.service import UserService
from authentication.auth_classes import JWTAuthCookie
# from scripts.worker import Task, queue_worker, schedule_worker
from notification import notification_provider
import schedule

purchase_service = PurchaseService()
rating_service = RatingService()
user_service = UserService()


@api_view(["POST"])
def create(request):
	amount = request.data.get("amount")
	gas_station = request.data.get("gas_station")
	company = request.data.get("company")
	vehicle = request.data.get("vehicle")
	balance_id = request.data.get("balance_id")

	if not amount:
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "no amount sent"})
	if not company:
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "no company sent"})
	if not vehicle:
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "no vehicle sent"})
	if not balance_id:
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "no balance_id sent"})
	if not gas_station:
		return Response(
			status=status.HTTP_400_BAD_REQUEST, data={"msg": "no gas_station sent"}
		)
	
	full_user = user_service.get_user(id=request.user.id)
	done, data = purchase_service.create(
		full_user, amount, gas_station, company, vehicle, balance_id
	)
	if not done:
		return Response(status=status.HTTP_417_EXPECTATION_FAILED, data=data)

	return Response(data={"purchase": data})


@api_view(['PUT'])
def purchase_done(request, purchase_id):
	fueltype_id = request.data.get('fueltypeId')
	if not fueltype_id or not str(fueltype_id).isdigit():
		return Response(status=status.HTTP_400_BAD_REQUEST, data={'msg': 'no valid fueltype id sent'})

	data, done = purchase_service.make_purchase_done(purchase_id, fueltype_id, request.user)
	if not done:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
	
	try:
		notification_provider.notificate_purchase_complete(data.get('fueltype'), data.get('purchase'))
	except Exception as e:
		print('from purchase_done:::', e)
		pass
		
	# schedule_worker.schedule(Task(run_notification), 1*60, just_once=True)
	return Response(data={'msg': 'done'})


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_purchases(request):
	from_date = request.GET.get("from")
	to_date = request.GET.get("to")
	max_amount = request.GET.get("max")
	min_amount = request.GET.get("min")
	gas_stations = request.GET.getlist("sts")
	user = request.user
	if user.is_admin:
		return Response(
			data=purchase_service.get_purchase_company_filtered(
				user, from_date, to_date, min_amount, max_amount, gas_stations
			)
		)
	else:
		return Response(
			data=purchase_service.get_purchase_gas_station_filtered(
				user, from_date, to_date, min_amount, max_amount
			)
		)


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_recent_purchases_wapp(request):
	user = request.user
	if user.is_admin:
		return Response(data=purchase_service.get_last_puchases(user))
	else:
		return Response(data=purchase_service.get_last_puchases_gas_station(user))


@api_view(["GET"])
def get_user_purchases(request):
	page = int(request.GET.get("page"))
	from_date = request.GET.get("from")
	to_date = request.GET.get("to")
	gas_station = request.GET.get("gas")
	return Response(
		data=purchase_service.user_purchases(
			page, request.user, from_date, to_date, gas_station
		)
	)


@api_view(["GET"])
def get_purchase_by_id(request, id):
	is_done = request.GET.get("is_done")
	if is_done == None:
		return Response(data="The parameter is done is required", status=500)
	return Response(data=purchase_service.purchase_by_id(request.user, id, is_done == "true"))


@api_view(["DELETE"])
def cancel_purchase(request, id):
	return Response(data=purchase_service.delete_purchase(request.user, id))


@api_view(["POST"])
def rate_purchase(request, purchase_id):
	rating = request.data.get("rating")
	comment = request.data.get("comment")
	if not rating or not str(rating).isdigit():
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "no valid rating sent"})
	if comment:
		comment = comment if len(comment) > 3 else None

	rating = rating if (int(rating) <= 5 and int(rating) > 0) else 5

	try:
		rating_service.rate_purchase(
			purchase_id=purchase_id, user=request.user, rating=int(rating), comment=comment
		)
	except:
		pass

	try:
		rating_service.update_ratings()
	except Exception as e:
		print(e)
		pass
	# queue_worker.add_task(task=Task(runner))
	return Response(data={"msg": "done"})

