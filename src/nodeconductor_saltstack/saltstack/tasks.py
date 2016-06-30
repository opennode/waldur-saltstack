from celery import shared_task

from .models import SaltStackServiceProjectLink
from ..sharepoint.tasks import sync_spl_quotas as sharepoint_sync_spl_quotas


# celerybeat tasks
@shared_task(name='nodeconductor.saltstack.sync_quotas')
def sync_quotas():
    for spl in SaltStackServiceProjectLink.objects.all():
        sharepoint_sync_spl_quotas.delay(spl.id)
