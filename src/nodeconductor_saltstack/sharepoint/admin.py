from django.contrib import admin, messages
from django.contrib.admin.options import ModelAdmin
from django.utils.translation import ungettext
from nodeconductor.core.models import SynchronizationStates

from nodeconductor.core.tasks import send_task
from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin
from .models import SharepointTenant, Template, SiteCollection, User


class SharepointTenantAdmin(structure_admin.PublishableResourceAdmin):
    inlines = [QuotaInline]

    actions = ['pull_users', 'sync_site_collections']

    def sync_site_collections(self, request, queryset):
        tenant_uuids = [uuid.hex for uuid in queryset.values_list('uuid', flat=True)]
        tasks_scheduled = queryset.count()

        send_task('sharepoint', 'sync_site_collection_quotas')(tenant_uuids)

        message = ungettext(
            'One tenant site collections scheduled for sync',
            '%(tasks_scheduled)d enant site collections scheduled for sync',
            tasks_scheduled)
        message = message % {'tasks_scheduled': tasks_scheduled}

        self.message_user(request, message)

    def pull_users(self, request, queryset):
        selected_tenants = queryset.count()
        queryset = queryset.filter(state=SynchronizationStates.IN_SYNC)
        tentants_uuids = [uuid.hex for uuid in queryset.values_list('uuid', flat=True)]
        send_task('sharepoint', 'pull_tenant_users')(tentants_uuids)

        tasks_scheduled = queryset.count()
        if selected_tenants != tasks_scheduled:
            message = 'Only in sync tenants can be scheduled for users pull'
            self.message_user(request, message, level=messages.WARNING)

        message = ungettext(
            'One tenant scheduled for users pull',
            '%(tasks_scheduled)d tenants scheduled for users pull',
            tasks_scheduled)
        message = message % {'tasks_scheduled': tasks_scheduled}

        self.message_user(request, message)

    pull_users.short_description = "Pull users for selected tenants"


class SiteCollectionAdmin(ModelAdmin):
    inlines = [QuotaInline]

    list_display = ('name', 'access_url', 'type', 'template')


admin.site.register(SharepointTenant, SharepointTenantAdmin)
admin.site.register(Template)
admin.site.register(SiteCollection, SiteCollectionAdmin)
admin.site.register(User)
