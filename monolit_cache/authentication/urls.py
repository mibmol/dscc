from django.urls import path
from . import views

urlpatterns = [
	path("check/", views.check),
	path("local/", views.auth_local),
]
