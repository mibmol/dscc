from django.urls import path
from . import views

urlpatterns = [
	path("station/<int:id>/", views.get_station),
	path("search/gs/", views.search_stations_query),
	path("search/gs/nearto/", views.search_near),
	path("all/", views.get_all_companies),
	path("stations/<int:idcompany>/", views.get_stations_company),
]
