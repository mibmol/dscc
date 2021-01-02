from django.db import models

class FuelType(models.Model):
	name = models.CharField(max_length=100)
	price_per_gallon = models.FloatField(default=0.0)
	created_at = models.DateTimeField(auto_now_add=True)
	since_date = models.DateTimeField()
	is_current = models.BooleanField(default=True)
	company = models.ForeignKey("company.Company", on_delete=models.SET_NULL, null=True)


class Purchase(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	amount = models.FloatField()
	gallons = models.FloatField(null=True)
	qrcode_string = models.CharField(max_length=2000, null=True)
	number_code = models.CharField(max_length=100, null=True)
	code_expiry_date = models.DateTimeField(null=True)
	is_done = models.BooleanField(default=False)
	user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
	gas_station = models.ForeignKey("company.GasStation", on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey("company.Company", on_delete=models.SET_NULL, null=True)
	vehicle = models.ForeignKey('users.VehiclesId', on_delete=models.DO_NOTHING, null=True)
	direct_buy_with_card = models.BooleanField(default=True) ## If the purchase was done in a station with Touch screen.
															 ## Default to True, which means if purchase was done in app 
															 ## you should put to False manually


class PurchaseFuelType(models.Model):
	fuel_type = models.ForeignKey("purchase.FuelType", on_delete=models.SET_NULL, null=True)
	purchase = models.ForeignKey("purchase.Purchase", on_delete=models.SET_NULL, null=True)


class PurchaseRating(models.Model):
	user = models.ForeignKey("users.User", on_delete=models.DO_NOTHING)
	created_at = models.DateTimeField(auto_now_add=True)
	purchase = models.ForeignKey("purchase.Purchase", on_delete=models.DO_NOTHING)
	rating = models.IntegerField(default=0)
	comment = models.CharField(max_length=1000)