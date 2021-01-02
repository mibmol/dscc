from math import trunc
from rest_framework import serializers
from .models import User, UserStation, VehiclesId, UserGasStationBalance
from company.serializers import CompanyBasicSerializer, GasStationSerializer
from company.models import TipAd
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


class VehiclesIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclesId
        fields = ["id", "number", "alias", "deleted"]


class GetBillingDataSerializer(serializers.ModelSerializer):

    vehicles_ids = VehiclesIdSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "cedula",
            "city",
            "address",
            "phone_number",
            "vehicles_ids",
        ]


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


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGasStationBalance
        fields = "__all__"


class GetUserGasStationBalance(serializers.ModelSerializer):
    company = CompanyBasicSerializer(read_only=True)
    gas_station = GasStationSerializer(read_only=True)

    class Meta:
        model = UserGasStationBalance
        fields = ["id", "total", "company", "gas_station"]

class ReportUserGasStationBalance(serializers.ModelSerializer):
    gas_station = BasicGasStationSerializer(read_only=True)
    user = GetUserSerializer(read_only=True)

    class Meta:
        model = UserGasStationBalance
        fields = ["id", "total", "gas_station", "user"]


class UpdateUserSerializer(serializers.ModelSerializer):
    """
        Serializer for update all user in system.
        Can't manage roles.
    """

    vehicles_ids = VehiclesIdSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "cedula",
            "address",
            "phone_number",
            "city",
            "vehicles_ids",
        ]


class BasicDataUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class CompleteTipAdSerializer(serializers.ModelSerializer):

    gas_station = BasicGasStationSerializer(read_only=True)
    created_by = BasicDataUserSerializer(read_only=True)

    class Meta:
        model = TipAd
        fields = "__all__"


class BasicTipAdSerializer(serializers.ModelSerializer):
    created_by = BasicDataUserSerializer(read_only=True)

    class Meta:
        model = TipAd
        fields = [
            "id",
            "kind",
            "created_at",
            "created_by",
            "title",
            "description",
            "img_path",
            "like_count",
            "dislike_count",
        ]


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


class UserStationSerializer(serializers.ModelSerializer):
    user = BasicDataUserSerializer(read_only=True)

    class Meta:
        model = UserStation
        fields = "__all__"
