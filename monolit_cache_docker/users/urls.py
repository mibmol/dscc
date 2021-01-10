from django.urls import path
from . import views

urlpatterns = [
	path("signup/", views.signup),
	path("signup/facebook/", views.signup_facebook),
	path("billing/data/", views.BillingData.as_view()),
	path("search/", views.user_search),
]
