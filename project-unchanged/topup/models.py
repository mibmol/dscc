from django.db import models


class TopUp(models.Model):
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("users.User", on_delete=models.DO_NOTHING)
    company = models.ForeignKey("company.Company", on_delete=models.DO_NOTHING)
    gas_station = models.ForeignKey("company.GasStation", on_delete=models.DO_NOTHING)


class TopUpTransfer(models.Model):
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_balance = models.ForeignKey(
        "users.UserGasStationBalance", on_delete=models.DO_NOTHING
    )
    receiver_user = models.ForeignKey(
        "users.User", related_name="receiver_user", on_delete=models.DO_NOTHING
    )
    sender_user = models.ForeignKey("users.User", on_delete=models.DO_NOTHING, null=True)
    company = models.ForeignKey("company.Company", on_delete=models.DO_NOTHING)
    gas_station = models.ForeignKey("company.GasStation", on_delete=models.DO_NOTHING)

