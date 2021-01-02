from django.urls import path
from . import views

urlpatterns = [
	path("signup/", views.signup),
	path("signup/facebook/", views.signup_facebook),
	path("admin/update/", views.update_user),
	path("billing/data/", views.BillingData.as_view()),
	path("balances/", views.BalanceData.as_view()),
	path('vehicles/', views.get_vehicles),
	path("company/", views.get_users_company),
	path("search/", views.user_search),
	path("status/change/", views.change_status),
	path("reset/password/", views.reset_password),
	path('reset/<uidb64>/<token>', views.CompletePasswordReset.as_view(), name="reset-user-password"),
	path("reset/password/done/", views.reset_password_done, name="reset-password-done"),
	path("reset/password/error/", views.reset_password_error, name="reset-password-error"),
]
