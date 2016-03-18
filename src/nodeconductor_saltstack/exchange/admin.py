from django.contrib import admin, messages
from django.utils.translation import ungettext

from nodeconductor.core.models import SynchronizationStates
from nodeconductor.core.tasks import send_task
from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin

from .models import ExchangeTenant, User, Group, Contact


class ExchangeTenantAdmin(structure_admin.PublishableResourceAdmin):
    inlines = [QuotaInline]

    actions = ['pull_users', 'sync_quotas']

    def sync_quotas(self, request, queryset):
        tenant_uuids = [uuid.hex for uuid in queryset.values_list('uuid', flat=True)]
        tasks_scheduled = queryset.count()

        send_task('exchange', 'sync_tenant_quotas')(tenant_uuids)

        message = ungettext(
            'One tenant cheduled for quotas sync',
            '%(tasks_scheduled)d tenant scheduled for quotas sync',
            tasks_scheduled)
        message = message % {'tasks_scheduled': tasks_scheduled}

        self.message_user(request, message)

    sync_quotas.short_description = 'Sync quotas for selected tenants'

    def pull_users(self, request, queryset):
        selected_tenants = queryset.count()
        queryset = queryset.filter(state=SynchronizationStates.IN_SYNC)
        tentants_uuids = [uuid.hex for uuid in queryset.values_list('uuid', flat=True)]
        send_task('exchange', 'pull_tenant_users')(tentants_uuids)

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


admin.site.register(ExchangeTenant, ExchangeTenantAdmin)
admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Group)
