from company.views import delete_gas_station, update_gas_station
from django.urls import path
from . import views

urlpatterns = [
	path("administrators/", views.get_all_company_users),
	path("station/<int:id>/", views.get_station),
	path("stations/", views.get_all_gas_stations_company),
	path("stations/detail/", views.get_all_gas_stations_company_detail),
	path("stations/create/", views.post_gas_station),
	path("stations/update/", views.update_gas_station),
	path("stations/delete/<int:id>/", views.delete_gas_station),
	path("tipads/", views.get_all_tipads),
	path('tipads/ads/', views.get_ads_app_user),
	path("tipads/tips/", views.get_tips_app_user),
	path("tipads/tips/old/", views.get_tips_old_app_user),
	path('tipads/tips/liked/', views.get_liked_tips),
	path("tipads/<int:id>/", views.get_tipad),
	path("tipads/<int:tipadid>/like/", views.tipad_like),
	path("tipads/<int:tipadid>/dislike/", views.tipad_dislike),
	path("policies/", views.get_policies),
	path("policies/create/", views.post_policies),
	path("policies/update/", views.update_policies),
	path("tipad/post/", views.post_tip_ad),
	path("search/gs/", views.search_stations_query),
	path("search/gs/nearto/", views.search_near),
	path("all/", views.get_all_companies),
	path("stations/<int:idcompany>/", views.get_stations_company),
	path("fuel/", views.get_fuel_types_gas_station),
	path("report/", views.report_generate_view)
]
