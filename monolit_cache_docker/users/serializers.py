from math import trunc
from rest_framework import serializers
from .models import User
from company.serializers import CompanyBasicSerializer, GasStationSerializer
from company.serializers import BasicGasStationSerializer


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "has_provided_password"]

    def save(self):
        user = User.objects.create_user(**self.validated_data)
        return user


class CreateUserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "has_provided_password",
            "is_admin",
            "is_gas_station_admin",
            "cedula",
            "address",
            "phone_number",
        ]

    def save(self):
        user = User.objects.create_user(**self.validated_data)
        return user


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]



class UpdateBillingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "cedula",
            "city",
            "address",
            "phone_number",
        ]



class BasicDataUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]



class UserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
        ]

