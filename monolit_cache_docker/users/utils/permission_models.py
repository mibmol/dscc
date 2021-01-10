PERMISSION_MODELS = {
    "company": {
        "company": (
            ("can_view_company", "puede ver compañía"),
            ("can_change_company", "puede cambiar compañía")
        ),
        "gas_station": (
            ("can_view_gas_station", "puede ver estaciones de servicio"),
            ("can_change_gas_station", "puede cambiar estaciones de servicio"),
            ("can_delete_gas_station", "puede eliminar estaciones de servicio"),
            ("can_add_gas_station", "puede agregar estaciones de servicio")
        )
    },
    "users": {
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