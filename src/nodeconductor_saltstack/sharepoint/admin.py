from django.contrib import admin

from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin
from .models import SharepointTenant, Template, SiteCollection, User


class SharepointTenantAdmin(structure_admin.ResourceAdmin):
    inlines = [QuotaInline]


admin.site.register(SharepointTenant, SharepointTenantAdmin)

admin.site.register(Template)
admin.site.register(SiteCollection)
admin.site.register(User)
