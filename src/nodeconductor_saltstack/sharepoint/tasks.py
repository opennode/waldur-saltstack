import binascii
import os

from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from .models import SharepointTenant, SiteCollection, Template, User
from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink


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
def initialize_tenant(tenant_uuid, template_uuid, user_uuid, storage, main_name, main_description):
    """ Create main, admin and personal site collections for tenant """
    tenant = SharepointTenant.objects.get(uuid=tenant_uuid)
    template = Template.objects.get(uuid=template_uuid)
    user = User.objects.get(uuid=user_uuid)

    try:
        backend = tenant.get_backend()
        data = {
            'name': main_name,
            'description': main_description,
            'template_code': template.code,
            'storage': storage,
            'user_count': tenant.quotas.get(name=tenant.Quotas.user_count).limit,
            'admin_id': user.admin_id,
        }
        backend_collections_details = backend.site_collections.create_main(**data)
    except SaltStackBackendError:
        tenant.initialization_status = tenant.InitializationStatuses.FAILED
        tenant.save()
        raise
    else:
        # main site collection
        main = SiteCollection.objects.create(
            name=data['name'],
            description=data['description'],
            template=template,
            access_url=backend_collections_details.main_site_collection_url,
            user=user,
        )
        storage = backend_collections_details.main_site_collection_storage
        main.set_quota_limit(SiteCollection.Quotas.storage, storage)
        tenant.add_quota_usage(SharepointTenant.Quotas.storage, storage)
        tenant.main_site_collection = main

        template_code = backend_collections_details.admin_site_collection_template_code
        admin = SiteCollection.objects.create(
            name=SiteCollection.Defaults.admin_site_collection['name'],
            description=SiteCollection.Defaults.admin_site_collection['description'],
            access_url=backend_collections_details.admin_site_collection_url,
            user=user,
            template=Template.objects.filter(
                code=template_code, settings=tenant.service_project_link.service.settings).first(),
        )
        storage = backend_collections_details.admin_site_collection_storage
        admin.set_quota_limit(SiteCollection.Quotas.storage, storage)
        tenant.add_quota_usage(SharepointTenant.Quotas.storage, storage)
        tenant.admin_site_collection = admin

        template_code = backend_collections_details.personal_site_collection_template_code
        personal = SiteCollection.objects.create(
            name=SiteCollection.Defaults.personal_site_collection['name'],
            description=SiteCollection.Defaults.personal_site_collection['description'],
            access_url=backend_collections_details.personal_site_collection_url,
            user=user,
            template=Template.objects.filter(
                code=template_code, settings=tenant.service_project_link.service.settings).first(),
        )
        storage = backend_collections_details.personal_site_collection_storage
        personal.set_quota_limit(SiteCollection.Quotas.storage, storage)
        tenant.add_quota_usage(SharepointTenant.Quotas.storage, storage)
        tenant.personal_site_collection = personal

        tenant.initialization_status = tenant.InitializationStatuses.INITIALIZED
        tenant.save()
