from django.db import models


class Company(models.Model):
	ruc = models.CharField(max_length=100)
	trade_name = models.CharField(max_length=300)
	business_name = models.CharField(
		max_length=300, null=True
	)  # es-ES: razon social, nombre legal.
	img_path = models.CharField(max_length=1000, null=True)
	email = models.EmailField(unique=True, null=True)
	company_logo_path = models.CharField(max_length=200)
	address = models.CharField(max_length=200, null=True)  # headquarter


class GasStation(models.Model):
	ruc = models.CharField(max_length=100)
	name = models.CharField(max_length=100)
	latitude = models.FloatField(null=True)
	longitude = models.FloatField(null=True)
	address = models.CharField(max_length=200)
	is_pilot = models.BooleanField(default=False)
	company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
	global_purchase_rating = models.FloatField(default=0.0)

