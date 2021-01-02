from django.urls import path
from . import views

urlpatterns = [
	path("create/", views.create),
	path('<int:purchase_id>/done/', views.purchase_done),
	path("company/", views.get_purchases),
	path("company/recent/", views.get_recent_purchases_wapp),
	path("user/", views.get_user_purchases),
	path("user/<int:id>/", views.get_purchase_by_id),
	path("delete/<int:id>/", views.cancel_purchase),
	path('rate/<int:purchase_id>/', views.rate_purchase),
]
