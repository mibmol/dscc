from django.urls import path
from . import test
from . import views

urlpatterns = [
	path("", views.notifications),
	path("old/", views.notifications_old),
	path("test/", test.notificate),
	path("test2/", test.notificate2),
	path("test3/", test.notificate3),
	path("test4/", test.notificate4),
	path("test5/", test.notificate5),
	path("user/token/", views.UserToken.as_view())
]
