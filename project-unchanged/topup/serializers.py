from rest_framework import serializers
from .models import TopUp, TopUpTransfer
from company.serializers import BasicGasStationSerializer
from users.serializers import BasicDataUserSerializer, GetUserSerializer


class TopUpSerializer(serializers.ModelSerializer):
    gas_station = BasicGasStationSerializer(read_only=True)
    user = BasicDataUserSerializer(read_only=True)

    class Meta:
        model = TopUp
        fields = ["id", "amount", "created_at", "user", "gas_station"]


class TransferSerializer(serializers.ModelSerializer):
    receiver_user = GetUserSerializer(read_only=True)
    sender_user = GetUserSerializer(read_only=True)
    gas_station = BasicGasStationSerializer(read_only=True)

    class Meta:
        model = TopUpTransfer
        fields = ["id", "amount", "created_at", "receiver_user", "sender_user", "gas_station"]
