from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from .models import SharepointTenant


@shared_task(name='nodeconductor.sharepoint.provision')
def provision(tenant_uuid, **kwargs):
    tenant = SharepointTenant.objects.get(uuid=tenant_uuid)
    chain(
        sync_service_project_links.s(tenant.service_project_link.to_string(), initial=True),
        provision_tenant.si(tenant_uuid, **kwargs),
    ).apply_async(
        link=set_online.si(tenant_uuid),
        link_error=set_erred.si(tenant_uuid))


@shared_task(name='nodeconductor.sharepoint.destroy')
@transition(SharepointTenant, 'begin_deleting')
@save_error_message
def destroy(tenant_uuid, transition_entity=None):
    tenant = transition_entity
    try:
        backend = tenant.get_backend()
        backend_tenant = backend.tenants.delete(tenant=tenant.name, domain=tenant.domain)
        backend_tenant.destroy()
    except:
        set_erred(tenant_uuid)
        raise
    else:
        tenant.delete()


@shared_task(is_heavy_task=True)
@transition(SharepointTenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    backend.pull_templates()
    backent_tenant = backend.tenants.create(
        tenant=tenant.name,
        domain=tenant.domain)

    tenant.backend_id = backent_tenant.id
    tenant.save()


@shared_task
@transition(SharepointTenant, 'set_online')
def set_online(tenant_uuid, transition_entity=None):
    tenant = transition_entity
    tenant.start_time = timezone.now()
    tenant.save(update_fields=['start_time'])


@shared_task
@transition(SharepointTenant, 'set_erred')
def set_erred(tenant_uuid, transition_entity=None):
    pass
