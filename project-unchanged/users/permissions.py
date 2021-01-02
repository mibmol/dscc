from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGasStationAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_gas_station_admin)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin)

class IsActive(BasePermission):

    message = "User is disabled"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)
