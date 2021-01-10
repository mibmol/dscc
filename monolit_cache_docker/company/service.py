from .models import Company, GasStation
from users.models import User
from .serializers import (
    BasicGasStationSerializer,
    CompanyBasicSerializer,
    GasStationSerializer,
    GasStationNestedSerializer,
    CoordSerializer,
)
import json
from rest_framework.exceptions import APIException
from datetime import datetime
from math import e, sqrt
import redis

rds = redis.Redis(host="localhost", port=6379)


class CompanyService:
    def get_station(self, station_id: int):
        key = "station" + str(station_id)

        if not station_id:
            return None
        station = None
        cache = rds.get(key)
        if not cache:
            try:
                result = GasStation.objects.prefetch_related("company").get(id=station_id)
                station = GasStationNestedSerializer(result).data
                rds.set(key, json.dumps(station))
            except:
                return station
        else:
            station = json.loads(cache)

        return station

    def __get_json__(self, i):
        return {
            "first_name": i.user.first_name,
            "last_name": i.user.last_name,
            "email": i.user.email,
            "is_active": i.user.is_active,
            "is_admin": i.user.is_admin,
            "phone_number": i.user.phone_number,
            "cedula": i.user.cedula,
            "is_gas_station_admin": i.user.is_gas_station_admin,
            "city": i.user.city,
            "address": i.user.address,
            "role": i.user.groups.all()[0].name,
            "id": i.user.pk,
        }

    def __gas_station_in_users__(self, gas_id, users):
        out = []
        for user in users:
            if user["gas_station"] == gas_id:
                out.append(user["user"])
        return out

    def get_companies(self):
        companies = Company.objects.all()
        serializer = CompanyBasicSerializer(companies, many=True)
        return serializer.data

    def get_gas_stations_company(self, id):
        gas_stations = GasStation.objects.filter(company__id=id)
        serializer = BasicGasStationSerializer(gas_stations, many=True)
        return serializer.data


def search_stations(text="", limit=4):
    stations = GasStation.objects.raw(
        """
        select 
            *
        from 
            company_gasstation
        where 
            match(name, address) against(%s IN BOOLEAN MODE)
        LIMIT %s;
    """,
        [text.lower() + "*", limit],
    )

    return GasStationSerializer(stations, many=True).data


DEFAULT_COORD_LAT = -2.171499
DEFAULT_COORD_LNG = -79.891971


def search_near_to(coord, limit=7):
    serializer = CoordSerializer(data=coord)
    if not serializer.is_valid():
        return []
    lat = coord.get("latitude", DEFAULT_COORD_LAT)
    lng = coord.get("longitude", DEFAULT_COORD_LNG)

    stations = GasStation.objects.all()
    serializer = GasStationSerializer(stations, many=True)
    with_distances = []
    for station in serializer.data:
        _lat = station.get("latitude")
        _lng = station.get("longitude")
        d = sqrt((_lat - lat) ** 2 + (_lng - lng) ** 2)
        with_distances.append({"station": station, "distance": d})
    with_distances.sort(key=lambda e: e["distance"])
    with_distances = with_distances[:limit]
    return [wd.get("station") for wd in with_distances]

