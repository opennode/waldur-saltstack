from celery import shared_task
from .models import SaltStackServiceProjectLink

from ..exchange.tasks import sync_tenant_quotas as exchange_sync_tenant_quotas
from ..exchange.tasks import sync_spl_quotas as exchange_sync_spl_quotas
from ..exchange.models import ExchangeTenant

from ..sharepoint.tasks import sync_spl_quotas as sharepoint_sync_spl_quotas


# celerybeat tasks
@shared_task(name='nodeconductor.saltstack.sync_quotas')
def sync_quotas():
    for tenant in ExchangeTenant.objects.filter(state=ExchangeTenant.States.ONLINE):
        exchange_sync_tenant_quotas.delay(tenant.uuid.hex)

    for spl in SaltStackServiceProjectLink.objects.all():
        exchange_sync_spl_quotas.delay(spl.id)
        sharepoint_sync_spl_quotas.delay(spl.id)


