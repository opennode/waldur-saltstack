from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from .models import SharepointTenant
from nodeconductor_saltstack.saltstack.models import SaltStackServiceProjectLink


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
def destroy(tenant_uuid, force=False):
    if force:
        error_callback = delete.si(tenant_uuid)
    else:
        error_callback = set_erred.si(tenant_uuid)
        tenant = SharepointTenant.objects.get(uuid=tenant_uuid)
        tenant.begin_deleting()
        tenant.save()

    schedule_deletion.apply_async(
        args=(tenant_uuid,),
        link=delete.si(tenant_uuid),
        link_error=error_callback,
    )


@shared_task
@save_error_message
def schedule_deletion(tenant_uuid):
    tenant = SharepointTenant.objects.get(uuid=tenant_uuid)
    backend = tenant.get_backend()
    raise Exception('test')
    backend.tenants.delete()


@shared_task(is_heavy_task=True)
@transition(SharepointTenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    backend_tenant = backend.tenants.create(
        tenant=tenant.name,
        domain=tenant.domain,
        name=tenant.site_name,
        description=tenant.description,
        storage_size=tenant.storage_size,
        users_count=kwargs['users_count'],
        template_code=kwargs['template_code'])

    tenant.backend_id = backend_tenant.id
    tenant.site_url = backend_tenant.base_url
    tenant.admin_url = backend_tenant.admin_url
    tenant.admin_login = backend_tenant.admin_login
    tenant.admin_password = backend_tenant.admin_password
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


@shared_task
def delete(tenant_uuid):
    SharepointTenant.objects.get(uuid=tenant_uuid).delete()


@shared_task
def sync_spl_quotas(spl_id):
    spl = SaltStackServiceProjectLink.objects.get(id=spl_id)
    tenants = SharepointTenant.objects.filter(service_project_link=spl)
    spl.set_quota_usage('sharepoint_storage', sum([t.storage_size for t in tenants]))
    spl.set_quota_usage('sharepoint_tenant_number', tenants.count())
