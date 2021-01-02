from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path("auth/", include("authentication.urls")),
	path("users/", include("users.urls")),
	path("company/", include("company.urls")),
	path("notification/", include("notification.urls")),
	path("topup/", include("topup.urls")),
	path("purchase/", include("purchase.urls")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.ADMIN_ENABLED:
	urlpatterns += [path("admin/", admin.site.urls)]
