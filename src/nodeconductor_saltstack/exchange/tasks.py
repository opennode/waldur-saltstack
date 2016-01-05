from celery import shared_task, chain
from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from ..saltstack.models import SaltStackServiceProjectLink
from .models import ExchangeTenant, User


@shared_task(name='nodeconductor.exchange.provision')
def provision(tenant_uuid, **kwargs):
    tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
    chain(
        sync_service_project_links.s(tenant.service_project_link.to_string(), initial=True),
        provision_tenant.si(tenant_uuid, **kwargs),
        sync_tenant_quotas.si(tenant_uuid),
    ).apply_async(
        link=set_online.si(tenant_uuid),
        link_error=set_erred.si(tenant_uuid))


@shared_task(name='nodeconductor.exchange.destroy')
@transition(ExchangeTenant, 'begin_deleting')
@save_error_message
def destroy(tenant_uuid, force=False, transition_entity=None):
    tenant = transition_entity
    try:
        backend = tenant.get_backend()
        backend.tenants.delete()
    except:
        if not force:
            set_erred(tenant_uuid)
            raise

    tenant.delete()


@shared_task(is_heavy_task=True)
@transition(ExchangeTenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    backent_tenant = backend.tenants.create(
        tenant=tenant.name,
        domain=tenant.domain,
        mailbox_size=tenant.mailbox_size,
        max_users=tenant.max_users)

    tenant.backend_id = backent_tenant.id
    tenant.save()


@shared_task
@transition(ExchangeTenant, 'set_online')
def set_online(tenant_uuid, transition_entity=None):
    tenant = transition_entity
    tenant.start_time = timezone.now()
    tenant.save(update_fields=['start_time'])


@shared_task
@transition(ExchangeTenant, 'set_erred')
def set_erred(tenant_uuid, transition_entity=None):
    pass


@shared_task
def sync_tenant_quotas(tenant_uuid):
    tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
    users = list(User.objects.filter(tenant=tenant))
    tenant.set_quota_usage('user_count', len(users))
    tenant.set_quota_usage('global_mailbox_size', sum(user.mailbox_size for user in users))


@shared_task
def sync_spl_quotas(spl_id):
    spl = SaltStackServiceProjectLink.objects.get(id=spl_id)
    tenants = ExchangeTenant.objects.filter(service_project_link=spl)
    spl.set_quota_usage('exchange_storage', sum([t.max_users * t.mailbox_size for t in tenants]))


# celerybeat tasks
@shared_task(name='nodeconductor.exchange.sync_quotas')
def sync_quotas():
    for tenant in ExchangeTenant.objects.filter(state=ExchangeTenant.States.ONLINE):
        sync_tenant_quotas.delay(tenant.uuid.hex)

    for spl in SaltStackServiceProjectLink.objects.all():
        sync_spl_quotas.delay(spl.id)
