from django.urls import path
from . import views

urlpatterns = [
	path("check/", views.check),
	path('check/wapp/', views.check_wapp),
	path("local/", views.auth_local),
	path("local/wapp/", views.auth_local_wapp),
	path('logout/wapp/', views.logout_wapp)
]
