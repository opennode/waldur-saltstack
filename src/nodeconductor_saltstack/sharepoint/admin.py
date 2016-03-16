from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.utils.translation import ungettext

from nodeconductor.core.tasks import send_task
from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin
from .models import SharepointTenant, Template, SiteCollection, User


class SharepointTenantAdmin(structure_admin.SaaSResourceAdmin):
    inlines = [QuotaInline]

    actions = ['sync_site_collections']

    def sync_site_collections(self, request, queryset):
        tenant_uuids = list(queryset.values_list('uuid', flat=True))
        tasks_scheduled = queryset.count()

        send_task('sharepoint', 'sync_site_collection_quotas')(tenant_uuids)

        message = ungettext(
            'One tenant site collections scheduled for sync',
            '%(tasks_scheduled)d enant site collections scheduled for sync',
            tasks_scheduled)
        message = message % {'tasks_scheduled': tasks_scheduled}

        self.message_user(request, message)


class SiteCollectionAdmin(ModelAdmin):
    inlines = [QuotaInline]

    list_display = ('name', 'access_url', 'type', 'template')


admin.site.register(SharepointTenant, SharepointTenantAdmin)
admin.site.register(Template)
admin.site.register(SiteCollection, SiteCollectionAdmin)
admin.site.register(User)
