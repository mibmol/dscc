from authentication.auth_classes import JWTAuthCookie
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from users.permissions import IsGasStationAdmin, IsSuperUser, IsCompanyAdmin
from users.service import UserService
from .service import TopupService, TransferService
from rest_framework.response import Response

topup_service = TopupService()
transfer_service = TransferService()
user_service = UserService()


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def company_topups_wapp(request):
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    max_amount = request.GET.get("max")
    min_amount = request.GET.get("min")
    gas_stations = request.GET.getlist("sts")
    user = request.user
    if user.is_admin:
        return Response(
            data=topup_service.get_topup_company_filtered(
                user, from_date, to_date, min_amount, max_amount, gas_stations
            )
        )
    else:
        return Response(
            data=topup_service.get_topup_gas_station_filtered(
                user, from_date, to_date, min_amount, max_amount
            )
        )


@api_view(["GET"])
@authentication_classes([JWTAuthCookie])
@permission_classes([IsCompanyAdmin | IsGasStationAdmin])
def company_recent_topups_wapp(request):
    user = request.user
    if user.is_admin:
        return Response(data=topup_service.get_last_topups(user))
    else:
        return Response(data=topup_service.get_last_topups_gas_station(user))


class TransferView(APIView):
    def get(self, request):
        get_all = request.GET.get("all")
        if get_all == "1":
            transfers = transfer_service.get_all_by_user(request.user)
            return Response(data={"transfers": transfers})

        transfer_id = request.GET.get("id")
        if transfer_id and f"{transfer_id}".isdigit():
            transfer = transfer_service.get_by_id(transfer_id)
            if not transfer:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"msg": "Transaction do not exist"}
                )
            return Response(data={"transfer": transfer})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"msg": "check the params"})

    def post(self, request):
        amount = request.data.get("amount")
        receiver = request.data.get("receiver")
        balance = request.data.get("balance")

        if not amount or not receiver or not balance:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"msg": "check the params"}
            )
        user = None
        if receiver.isdigit():
            user = user_service.get_user(cedula=receiver)
        else:
            user = user_service.get_user(email=receiver)

        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"msg": "Invalid receiver"})
        if not balance.get("id") or not f"{balance.get('id')}".isdigit():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"msg": "Invalid balance"}
            )

        if request.user.id == user.id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Can't transfers to yourself."},
            )

        balance = user_service.get_balance_by_id(balance.get("id"))
        if not balance:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"msg": "Invalid balance"})

        done, data = transfer_service.create_transfer(
            receiver_user=user, sender_user=request.user, amount=amount, balance=balance
        )
        if not done:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"msg": data.get("msg")}
            )

        return Response(data={"transfer": data})

