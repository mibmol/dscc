PERMISSION_MODELS = {
    "company": {
        "company_admin_user": (
            ("can_view_company_users", "puede ver usuarios de la compañía"),
            ("can_change_company_users", "puede cambiar usuarios de la compañía"),
            ("can_delete_company_users", "puede eliminar usuarios de la compañía"),
            ("can_add_company_users", "puede agregar usuarios de la compañía")
        ),
        "company": (
            ("can_view_company", "puede ver compañía"),
            ("can_change_company", "puede cambiar compañía")
        ),
        "gas_station": (
            ("can_view_gas_station", "puede ver estaciones de servicio"),
            ("can_change_gas_station", "puede cambiar estaciones de servicio"),
            ("can_delete_gas_station", "puede eliminar estaciones de servicio"),
            ("can_add_gas_station", "puede agregar estaciones de servicio")
        ),
        "policies":(
            ("can_view_policies", "puede ver políticas de privacidad"),
            ("can_change_policies", "puede cambiar políticas de privacidad"),
            ("can_delete_policies", "puede eliminar políticas de privacidad"),
            ("can_add_policies", "puede agregar políticas de privacidad")
        ),
        "tip_ad":(
            ("can_view_tip_ad", "puede ver tips y anuncios"),
            ("can_change_tip_ad", "puede cambiar tips y anuncios"),
            ("can_add_tip_ad", "puede agregar tips y anuncios")
        )
    },
    "purchase":{
        "fuel_type":(
            ("can_view_fuel_type", "puede ver tipos de combustible"),
            ("can_change_fuel_type", "puede cambiar tipos de combustible"),
            ("can_delete_fuel_type", "puede eliminar tipos de combustible"),
            ("can_add_fuel_type", "puede agregar tipos de combustible")
        ),
        "purchase_fuel_type": (
            ("can_view_purchase_fuel_type", "puede ver compras por tipo de combustible"),
        ),
        "purchase": (
            ("can_view_purchase", "puede ver compras"),
        )
    },
    "topup": {
        "top_up": (
            ("can_view_top_up", "puede ver recargas"),
        ),
        "top_up_transfer": (
            ("can_view_top_up_transfer", "puede ver transferencias de saldo"),
        )
    },
    "users": {
        "user_gas_station_balance": (
            ("can_view_company_balance", "puede ver balance de usario por compañía"),
        ),
        "user_station": (
            ("can_view_user_station", "puede ver usuarios de la compañía en estaciones de servicio"),
            ("can_change_user_station", "puede cambiar usuarios de la compañía en estaciones de servicio"),
            ("can_delete_user_station", "puede eliminar usuarios de la compañía en estaciones de servicio"),
            ("can_add_user_station", "puede agregar usuarios de la compañía en estaciones de servicio")
        ),
        "user": {
            ("can_view_user", "puede ver usuarios"),
            ("can_change_user_is_active", "puede habilitar/inhabilitar usuarios"),
            ("can_add_user", "puede agregar usuarios")
        }
    }
}

# model format: app.model
def getPermissionsByAppModel(model: str):
    app, model = tuple(model.split("."))
    return PERMISSION_MODELS[app][model]

def getPermissionsByQuery(query: str):
    
    return set()

# def generate_permissions():
#     for app in PERMISSION_MODELS:
#         models = PERMISSION_MODELS[app]
#         for model in models:
#             permissions = models[model]
#             for permission in permissions:
#                 permission_service.create_permission_model2(model=model, codename=permission[0], name=permission[1])