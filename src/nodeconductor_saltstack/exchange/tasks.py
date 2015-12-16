from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from .models import Tenant


@shared_task(name='nodeconductor.exchange.provision')
def provision(tenant_uuid, **kwargs):
    tenant = Tenant.objects.get(uuid=tenant_uuid)
    chain(
        sync_service_project_links.s(tenant.service_project_link.to_string(), initial=True),
        provision_tenant.si(tenant_uuid, **kwargs),
        sync_tenant_quotas.si(tenant_uuid),
    ).apply_async(
        link=set_online.si(tenant_uuid),
        link_error=set_erred.si(tenant_uuid))


@shared_task(name='nodeconductor.exchange.destroy')
@transition(Tenant, 'begin_deleting')
@save_error_message
def destroy(tenant_uuid, force=False, transition_entity=None):
    tenant = transition_entity
    try:
        backend = tenant.get_backend()
        backend.tenants.delete(tenant=tenant.name, domain=tenant.domain)
    except:
        if not force:
            set_erred(tenant_uuid)
            raise

    tenant.delete()


@shared_task(is_heavy_task=True)
@transition(Tenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    backent_tenant = backend.tenants.create(
        tenant=tenant.name,
        domain=tenant.domain,
        mailbox_size=backend.mb2gb(float(tenant.mailbox_size)),
        max_users=tenant.max_users)

    tenant.backend_id = backent_tenant.id
    tenant.save()
    tenant.quotas.create(name='user_count', limit=tenant.max_users, usage=0)
    tenant.quotas.create(name='global_mailbox_size', limit=tenant.mailbox_size, usage=0)


@shared_task
@transition(Tenant, 'set_online')
def set_online(tenant_uuid, transition_entity=None):
    tenant = transition_entity
    tenant.start_time = timezone.now()
    tenant.save(update_fields=['start_time'])


@shared_task
@transition(Tenant, 'set_erred')
def set_erred(tenant_uuid, transition_entity=None):
    pass


@shared_task
def sync_tenant_quotas(tenant_uuid):
    tenant = Tenant.objects.get(uuid=tenant_uuid)
    backend = tenant.get_backend()
    backend.sync_user_count_quota(tenant)
    backend.sync_mailbox_global_size_quotas(tenant)


# celerybeat tasks
@shared_task(name='nodeconductor.exchange.sync_tenants_quotas')
def sync_tenants_quotas():
    for tenant in Tenant.objects.filter(state=Tenant.States.ONLINE):
        sync_tenant_quotas.delay(tenant.uuid.hex)
