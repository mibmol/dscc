from rest_framework import exceptions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .service import CompanyService, search_near_to, search_stations

#from scripts.worker import queue_worker, Task

# Create your views here.

company_service = CompanyService()


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def get_station(request, idx):
	if not idx:
		return Response(status=status.HTTP_400_BAD_REQUEST)

	result = company_service.get_station(idx)
	if not result:
		return Response(status=status.HTTP_404_NOT_FOUND)
	return Response(data={"station": result})



@api_view(["GET"])
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


