from django.contrib import admin

from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin
from .models import Tenant


class TenantAdmin(structure_admin.ResourceAdmin):
    inlines = [QuotaInline]


admin.site.register(Tenant, TenantAdmin)
