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
    tenant.service_project_link.add_quota_usage('sharepoint_storage', -tenant.storage_size)


@shared_task(is_heavy_task=True)
@transition(SharepointTenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    backent_tenant = backend.tenants.create(
        tenant=tenant.name,
        domain=tenant.domain,
        name=tenant.site_name,
        description=tenant.description,
        storage_size=tenant.storage_size,
        users_count=kwargs['users_count'],
        template_code=kwargs['template_code'])

    tenant.backend_id = backent_tenant.id
    tenant.site_url = backent_tenant.site_url
    tenant.admin_url = backent_tenant.admin_url
    tenant.admin_login = backent_tenant.admin_login
    tenant.admin_password = backent_tenant.admin_password
    tenant.save()
    tenant.service_project_link.add_quota_usage('sharepoint_storage', tenant.storage_size)


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
