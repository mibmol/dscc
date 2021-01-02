from django.contrib import admin
from .models import User, VehiclesId, UserGasStationBalance, UserStation

admin.site.register(User)
admin.site.register(VehiclesId)
admin.site.register(UserGasStationBalance)
admin.site.register(UserStation)
