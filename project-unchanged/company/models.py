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
	bank_account_info = models.JSONField(
		null=True
	)  # es-ES: Cuenta bancaria, email, cedula, tipo_cuenta, dueño_de_la_cuenta, numero de cuenta
	address = models.CharField(max_length=200, null=True)  # headquarter


class CompanyAdminUser(models.Model):
	user = models.ForeignKey("users.User", on_delete=models.CASCADE)
	company = models.ForeignKey("company.Company", on_delete=models.CASCADE)


class GasStation(models.Model):
	ruc = models.CharField(max_length=100)
	name = models.CharField(max_length=100)
	latitude = models.FloatField(null=True)
	longitude = models.FloatField(null=True)
	address = models.CharField(max_length=200)
	is_pilot = models.BooleanField(default=False)
	company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
	global_purchase_rating = models.FloatField(default=0.0)


class Policies(models.Model):
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)
	company = models.ForeignKey("company.Company", on_delete=models.CASCADE)


class TipAd(models.Model):
	KINDS = [
		("TIP", "tip"),
		("AD", "advertisement"),
	]
	kind = models.CharField(choices=KINDS, max_length=4)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
	company = models.ForeignKey("company.Company", on_delete=models.SET_NULL, null=True)
	gas_station = models.ForeignKey("company.GasStation", on_delete=models.SET_NULL, null=True)
	title = models.CharField(max_length=200, null=True)
	description = models.CharField(max_length=2000, null=True)
	img_path = models.CharField(max_length=1000)
	like_count = models.IntegerField(default=0)
	dislike_count = models.IntegerField(default=0)


class UserTipAdLike(models.Model):
	user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, null=True)
	tipad = models.ForeignKey('company.TipAd', on_delete=models.DO_NOTHING, null=True)
	is_like = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)


class UserFeedback(models.Model):
	KINDS = [
		("S", "suggestion"),
		("B", "bug"),
		("F", "fraud"),
		("O", "other"),
	]
	img_path = models.CharField(max_length=1000)
	kind = models.CharField(choices=KINDS, max_length=2)
	created_at = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
	gas_station = models.ForeignKey("company.GasStation", on_delete=models.DO_NOTHING)
	description = models.CharField(max_length=2000, null=True)

