import binascii
import os

from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from .models import SharepointTenant, SiteCollection
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
    backend.tenants.delete()


@shared_task(is_heavy_task=True)
@transition(SharepointTenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    # generate a random name to be used as unique tenant id in MS Exchange
    # Example of formt: NC_28052BF28A
    tenant_backend_id = 'NC_%s' % binascii.b2a_hex(os.urandom(5)).upper()

    backend.tenants.create(
        backend_id=tenant_backend_id,
        domain=tenant.domain,
    )
    tenant.backend_id = tenant_backend_id
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


@shared_task
def initialize_tenant(tenant_uuid, main_site_collection_uuid, admin_site_collection_uuid, users_site_collection_uuid):
    tenant = SharepointTenant.objects.get(uuid=tenant_uuid)
    main_site_collection = SiteCollection.objects.get(uuid=main_site_collection_uuid)
    admin_site_collection = SiteCollection.objects.get(uuid=admin_site_collection_uuid)
    users_site_collection = SiteCollection.objects.get(uuid=users_site_collection_uuid)

    try:
        backend = tenant.get_backend()

        backend_site_collection = backend.site_collections.create_main(
            admin_id=main_site_collection.user.admin_id,
            template_code=main_site_collection.template.code,
            name=main_site_collection.name,
            description=main_site_collection.description,
            max_quota=main_site_collection.quotas.get(name=main_site_collection.Quotas.storage).limit,
            user_count=tenant.quotas.get(name=tenant.Quotas.user_count).limit,
        )
        main_site_collection.access_url = backend_site_collection.url
        main_site_collection.save()

        backend_site_collection = backend.site_collections.create(
            admin_id=admin_site_collection.user.admin_id,
            template_code=admin_site_collection.template.code,
            name=admin_site_collection.name,
            description=admin_site_collection.description,
            max_quota=admin_site_collection.quotas.get(name=main_site_collection.Quotas.storage).limit,
            site_url=admin_site_collection.site_url,
        )
        admin_site_collection.access_url = backend_site_collection.url
        admin_site_collection.save()

        backend_site_collection = backend.site_collections.create(
            admin_id=users_site_collection.user.admin_id,
            template_code=users_site_collection.template.code,
            name=users_site_collection.name,
            description=users_site_collection.description,
            max_quota=users_site_collection.quotas.get(name=main_site_collection.Quotas.storage).limit,
            site_url=users_site_collection.site_url,
        )
        users_site_collection.access_url = backend_site_collection.url
        users_site_collection.save()
    except:
        tenant.initialization_status = tenant.InitializationStatuses.FAILED
        tenant.save()
        raise
