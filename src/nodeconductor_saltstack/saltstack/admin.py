from django.contrib import admin

from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin
from .models import SaltStackServiceProjectLink, SaltStackService


class SaltStackServiceProjectLinkAdmin(structure_admin.ServiceProjectLinkAdmin):
    inlines = [QuotaInline]


admin.site.register(SaltStackService, structure_admin.ServiceAdmin)
admin.site.register(SaltStackServiceProjectLink, SaltStackServiceProjectLinkAdmin)
