from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .CustomUserManager import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    has_provided_billing_data = models.BooleanField(default=False)
    ## has_provided_password is false if the user signed up with social oauth
    # (just facebook for now)
    has_provided_password = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    cedula = models.CharField(unique=True, max_length=15, null=True)  ##  or passport
    is_gas_station_admin = models.BooleanField(default=False)
    city = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    devices = models.JSONField(null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} {self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        return self.is_admin


# abcd123 === abdc-123
class VehiclesId(models.Model):
    number = models.CharField(max_length=10, unique=False)
    alias = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="vehicles_ids"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)


# class UserCompanyBalance(models.Model):
# 	total = models.FloatField(default=0.0)
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
#     gas_station = models.ForeignKey(GasStation, on_delete=models.DO_NOTHING)


class UserGasStationBalance(models.Model):
    total = models.FloatField(default=0.0)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    gas_station = models.ForeignKey("company.GasStation", on_delete=models.DO_NOTHING)


class UserStation(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    gas_station = models.ForeignKey("company.GasStation", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

