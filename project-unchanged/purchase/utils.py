from datetime import datetime
from users.models import User
from purchase.models import Purchase
import math


def generate_qr_code_string(user: User, purchase: Purchase):
    items = [
        f"id: {purchase.id}",
        f"Cantidad: ${purchase.amount}",
        f"Usuario: {user.first_name} {user.last_name}",
        f"Cedula: {user.cedula}",
        f"Expiracion: {purchase.code_expiry_date} ",
        f"Estado: {'realizada' if purchase.is_done else 'no realizada'}",
    ]
    return " | ".join(items)


def generate_number_code(purchase_id):
    year = datetime.now().year
    return f"{purchase_id*2 + math.ceil(year/2)}-{purchase_id}"

