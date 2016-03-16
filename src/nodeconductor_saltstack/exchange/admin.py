from django.contrib import admin
from django.utils.translation import ungettext

from nodeconductor.core.tasks import send_task
from nodeconductor.quotas.admin import QuotaInline
from nodeconductor.structure import admin as structure_admin

from .models import ExchangeTenant, User, Group, Contact


class ExchangeTenantAdmin(structure_admin.PublishableResourceAdmin):
    inlines = [QuotaInline]

    actions = ['sync_quotas']

    def sync_quotas(self, request, queryset):
        tenant_uuids = list(queryset.values_list('uuid', flat=True))
        tasks_scheduled = queryset.count()

        send_task('exchange', 'sync_tenant_quotas')(tenant_uuids)

        message = ungettext(
            'One tenant cheduled for quotas sync',
            '%(tasks_scheduled)d tenant scheduled for quotas sync',
            tasks_scheduled)
        message = message % {'tasks_scheduled': tasks_scheduled}

        self.message_user(request, message)


admin.site.register(ExchangeTenant, ExchangeTenantAdmin)
admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Group)
