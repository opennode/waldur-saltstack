from django.contrib import admin

from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin
from .models import ExchangeTenant


class ExchangeTenantAdmin(structure_admin.ResourceAdmin):
    inlines = [QuotaInline]


admin.site.register(ExchangeTenant, ExchangeTenantAdmin)
