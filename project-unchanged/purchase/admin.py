from django.contrib import admin
from .models import FuelType, Purchase, PurchaseFuelType, PurchaseRating

admin.site.register(Purchase)
admin.site.register(FuelType)
admin.site.register(PurchaseFuelType)
admin.site.register(PurchaseRating)