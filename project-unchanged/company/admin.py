from django.contrib import admin
from .models import Company, GasStation, CompanyAdminUser, Policies, TipAd, UserFeedback

admin.site.register(Company)
admin.site.register(GasStation)
admin.site.register(CompanyAdminUser)
admin.site.register(Policies)
admin.site.register(TipAd)
admin.site.register(UserFeedback)
