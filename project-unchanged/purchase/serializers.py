from rest_framework import serializers
from .models import Purchase, FuelType, PurchaseFuelType, PurchaseRating
from company.serializers import BasicGasStationSerializer, GasStationSerializer, GasStationDetailSerializer
from users.serializers import BasicDataUserSerializer, VehiclesIdSerializer


class PurchaseSerializer(serializers.ModelSerializer):
    gas_station = BasicGasStationSerializer(read_only=True)
    user = BasicDataUserSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = ["created_at", "amount", "gallons", "gas_station", "user", "number_code", "is_done"]

class BasicPurchaseSerializer(serializers.ModelSerializer):
    gas_station = BasicGasStationSerializer(read_only=True)
    
    class Meta:
        model = Purchase
        fields = ["amount", "gas_station", "number_code"]

class PurchaseDetailSerializer(serializers.ModelSerializer):
    gas_station = GasStationDetailSerializer(read_only=True)
    vehicle = VehiclesIdSerializer(read_only=True)
    user = BasicDataUserSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = "__all__"

class PurchaseHistorySerializer(serializers.ModelSerializer):
    gas_station = BasicGasStationSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = ["id", "created_at", "code_expiry_date", "amount", "gas_station", "is_done"]


class CreatedPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = "__all__"


class FuelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelType
        fields = ["name", "price_per_gallon"]


class GetFuelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelType
        fields = ["id", "name", "price_per_gallon"]


class GetPurchaseFuelTypeSerializer(serializers.ModelSerializer):
    fuel_type = FuelTypeSerializer(read_only=True)
    purchase = PurchaseSerializer(read_only=True)

    class Meta:
        model = PurchaseFuelType
        fields = "__all__"

class PurchaseFuelTypeDetailSerializer(serializers.ModelSerializer):
    fuel_type = FuelTypeSerializer(read_only=True)
    purchase = PurchaseDetailSerializer(read_only=True)

    class Meta:
        model = PurchaseFuelType
        fields = "__all__"


class PurchaseRatingSerializer(serializers.ModelSerializer):

    user = BasicDataUserSerializer(read_only=True)
    purchase = BasicPurchaseSerializer(read_only=True)

    class Meta:
        model = PurchaseRating
        fields = "__all__"