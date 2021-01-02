from rest_framework import serializers
from .models import Company, GasStation, TipAd, Policies


class CompanyBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "business_name", "img_path", "company_logo_path", "address"]


class GasStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasStation
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.ruc = validated_data.get("ruc")
        instance.name = validated_data.get("name")
        instance.latitude = validated_data.get("latitude")
        instance.longitude = validated_data.get("longitude")
        instance.address = validated_data.get("address")
        instance.is_pilot = validated_data.get("is_pilot")
        instance.save()
        return instance


class GasStationNestedSerializer(serializers.ModelSerializer):
    company = CompanyBasicSerializer(read_only=True)

    class Meta:
        model = GasStation
        fields = [
            "id",
            "name",
            "address",
            "latitude",
            "longitude",
            "global_purchase_rating",
            "company",
        ]


class GasStationDetailSerializer(serializers.ModelSerializer):
    company = CompanyBasicSerializer(read_only=True)

    class Meta:
        model = GasStation
        fields = [
            "id",
            "name",
            "address",
            "company",
        ]


class BasicGasStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasStation
        fields = ["id", "ruc", "name", "address"]


class TipAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipAd
        fields = ['id', "created_at", "title", "description", "img_path"]


class TipAdSerializerAll(serializers.ModelSerializer):
    company = CompanyBasicSerializer(read_only=True)
    class Meta:
        model = TipAd
        fields = '__all__'


class PoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policies
        fields = ["id", "description"]


class CreateTipAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipAd
        fields = [
            "kind",
            "created_by",
            "company",
            "gas_station",
            "title",
            "description",
            "img_path",
        ]


class CoordSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

