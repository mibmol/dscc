from company.reports.report_provieder import CSV, HTML, PDF, XLSX, purchase_report, rating_report, topup_report, users_report
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from users.permissions import IsCompanyAdmin, IsGasStationAdmin

from rest_framework import exceptions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .service import CompanyService, TipAdService, search_near_to, search_stations
from authentication.auth_classes import JWTAuthCookie
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt

#from scripts.worker import queue_worker, Task

# Create your views here.

company_service = CompanyService()
tipad_service = TipAdService()


@api_view(["GET"])
def get_station(request, id):
	if not id:
		return Response(status=status.HTTP_400_BAD_REQUEST)

	result = company_service.get_station(id)
	if not result:
		return Response(status=status.HTTP_404_NOT_FOUND)
	return Response(data={"station": result})


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
def get_all_company_users(request):
	return Response(data=company_service.get_company_users(request.user))


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
def get_all_gas_stations_company(request):
	return Response(data=company_service.get_company_stations(request.user))


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
def get_all_gas_stations_company_detail(request):
	return Response(data=company_service.get_company_stations_detail(request.user))


@api_view(["POST"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
@csrf_exempt
def post_gas_station(request):
	return Response(data=company_service.create_gas_station(request.data, request.user))


@api_view(["PUT"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
@csrf_exempt
def update_gas_station(request):
	return Response(data=company_service.put_gas_station(request.data))


@api_view(["DELETE"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
def delete_gas_station(request, id):
	return Response(data=company_service.delete_gas_station(id))


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_all_tipads(request):
	user = request.user
	if user.is_admin:
		return Response(data=company_service.get_company_tipads(user))
	else:
		return Response(data=company_service.get_gas_station_tipads(user))


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_policies(request):
	return Response(data=company_service.get_compay_polices(request.user))


@api_view(["POST"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
@csrf_exempt
def post_policies(request):
	description = request.data.get("description")
	return Response(data=company_service.create_company_policies(request.user, description))


@api_view(["PUT"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin])
@csrf_exempt
def update_policies(request):
	idp = request.data.get("id")
	description = request.data.get("description")
	return Response(
		data=company_service.update_company_policies(request.user, idp, description)
	)


@api_view(["POST"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
@csrf_exempt
def post_tip_ad(request):
	user = request.user
	data = request.data
	file_i = request.FILES.get("image")
	return Response(data=tipad_service.create(user, data, file_i))


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_tipad(request, id):
	user = request.user
	if user.is_admin:
		return Response(data=tipad_service.get_tipad_company(id, user))
	else:
		return Response(data=tipad_service.get_tipad_gas_station(id, user))


@api_view(["GET"])
@cache_page(60 * 60 * 24)
def search_stations_query(request):
	q = request.GET.get("q")
	if not q:
		return Response(data={"result": []})
	results = search_stations(text=q)

	return Response(data={"result": results})


@api_view(["GET"])
def search_near(request):
	lat = request.GET.get("latitude")
	lng = request.GET.get("longitude")
	limit = request.GET.get("limit")
	if not lat or not lng:
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "No coords sent"})

	try:
		lat = float(lat)
		lng = float(lng)
	except:
		return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "Invalid coords"})

	result = []
	if limit and limit.isdigit():
		result = search_near_to(coord={"latitude": lat, "longitude": lng}, limit=int(limit))
	else:
		result = search_near_to(coord={"latitude": lat, "longitude": lng})

	return Response(data={"result": result})


@api_view(["GET"])
def get_all_companies(request):
	return Response(data=company_service.get_companies())


@api_view(["GET"])
def get_stations_company(request, idcompany):
	return Response(data=company_service.get_gas_stations_company(idcompany))


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def report_generate_view(request):
	from_date = request.GET.get("from")
	to_date = request.GET.get("to")
	gas_stations = request.GET.getlist("sts")
	fuel_types = request.GET.getlist('fts')
	is_active = request.GET.get('is_active')
	report = request.GET.get('type')

	if not report:
		return Response(data="Type report is required", status=500)

	if is_active != None:
		is_active = is_active == 'true'
	user = request.user

	if report == "0":
		return Response(data=purchase_report(user, from_date, to_date, gas_stations, fuel_types))
	elif report == "1":
		return Response(data=topup_report(user, from_date, to_date, gas_stations))
	elif report == "2":
		return Response(data=users_report(user, gas_stations=gas_stations, is_active=is_active))
	elif report == "3":
		return Response(data=rating_report(user, from_date, to_date, gas_stations))
	else:
		return Response(data="type report is not allowed")


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def get_fuel_types_gas_station(request):
	user = request.user
	return Response(data=company_service.get_fuel_types(user))


@api_view(['GET'])
def get_ads_app_user(request):
	results = tipad_service.get_ads_app()
	return Response(data={'ads': results})

@api_view(["GET"])
def get_tips_app_user(request):
	results = tipad_service.get_tips_app()
	if len(results) > 0:
		start = results[-1]["id"]
		end = results[0]["id"]
	else:
		start = 0
		end = 1
	likes = tipad_service.get_liked_tips(request.user, int(start) - 1, int(end) + 1)
	return Response(data={"tips": results, "likes": likes})


@api_view(["GET"])
def get_tips_old_app_user(request):
	last_id = request.GET.get("last")
	if not last_id or not str(last_id).isdigit():
		return Response(data={"tips": [], "liked": []})
	results = tipad_service.get_tips_app_old(last_id=last_id)
	if len(results) > 0:
		start = results[-1]["id"]
		end = results[0]["id"]
	else:
		start = 0
		end = 1
	likes = tipad_service.get_liked_tips(request.user, int(start) - 1, int(end) + 1)
	return Response(data={"tips": results, "likes": likes})


@api_view(["GET"])
def get_liked_tips(request):
	start = request.GET.get("start_id")
	end = request.GET.get("end_id")

	if not start or not end:
		return Response(
			status=status.HTTP_400_BAD_REQUEST,
			data={"msg": "start_id and end_id are required"},
		)
	if not start.isdigit() or not end.isdigit():
		return Response(
			status=status.HTTP_400_BAD_REQUEST,
			data={"msg": "start_id and end_id should be integers"},
		)
	results = tipad_service.get_liked_tips(request.user, int(start) - 1, int(end) + 1)
	return Response(data={"liked": results})


@api_view(["PUT"])
def tipad_like(request, tipadid):
	try:
		tipad_service.like_tipad(tipadid, request.user)
	except:
		pass

	# queue_worker.add_task(Task(runner))
	return Response(data={"msg": "yep"})


@api_view(["PUT"])
def tipad_dislike(request, tipadid):
	try:
		tipad_service.dislike_tipad(tipadid, request.user)
	except:
		pass

	# queue_worker.add_task(Task(runner))
	return Response(data={"msg": "yep"})

