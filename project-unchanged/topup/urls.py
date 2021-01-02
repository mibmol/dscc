from django.urls import path
from . import views

urlpatterns = [
    path("company/", views.company_topups_wapp),
    path("company/recent/", views.company_recent_topups_wapp),
    path("user/transfer/", views.TransferView.as_view()),
]
