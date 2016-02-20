import binascii
import os

from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition
from nodeconductor.structure.tasks import sync_service_project_links

from .models import SharepointTenant, SiteCollection, Template, User
from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from ..saltstack.utils import sms_user_password


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
def provision_tenant(tenant_uuid, transition_entity=None,
                     site_name=None, site_description=None, template_uuid=None, phone=None, notify=None, **kwargs):
    # Create tenant itself
    tenant = transition_entity
    backend = tenant.get_backend()
    # generate a random name to be used as unique tenant id in MS Exchange
    # Example of format: NC_28052BF28A
    tenant_backend_id = 'NC_%s' % binascii.b2a_hex(os.urandom(5)).upper()

    backend.tenants.create(
        backend_id=tenant_backend_id,
        domain=tenant.domain,
    )
    tenant.backend_id = tenant_backend_id
    tenant.save()

    # Create admin user
    backend = tenant.get_backend()  # get backend again to mark admin user as available
    admin_data = dict(email='admin@{}'.format(tenant.domain), **User.Defaults.admin)
    backend_admin = backend.users.create(**admin_data)

    admin = User.objects.create(
        tenant=tenant,
        backend_id=backend_admin.id,
        admin_id=backend_admin.admin_id,
        password=backend_admin.password,
        phone=phone or '',  # hotfix - phone cannot be None
        **admin_data
    )
    tenant.admin = admin
    admin.init_personal_site_collection(backend_admin.personal_site_collection_url)
    sms_user_password(admin)

    # Initialize default site collections
    template = Template.objects.get(uuid=template_uuid)
    backend_collections_details = backend.site_collections.create_main(
        admin_id=admin.admin_id,
        name=site_name,
        description=site_description,
        template_code=template.code,
        storage=SiteCollection.Defaults.main_site_collection['storage'],
    )

    main_sc = SiteCollection.objects.create(
        name=site_name,
        description=site_description,
        template=template,
        access_url=backend_collections_details.main_site_collection_url,
        user=admin,
        type=SiteCollection.Types.MAIN,
    )
    storage = backend_collections_details.main_site_collection_storage
    main_sc.set_quota_limit(SiteCollection.Quotas.storage, storage)
    tenant.main_site_collection = main_sc

    template_code = backend_collections_details.admin_site_collection_template_code
    admin_sc = SiteCollection.objects.create(
        name=SiteCollection.Defaults.admin_site_collection['name'],
        description=SiteCollection.Defaults.admin_site_collection['description'],
        access_url=backend_collections_details.admin_site_collection_url,
        user=admin,
        template=Template.objects.filter(
            code=template_code, settings=tenant.service_project_link.service.settings).first(),
        type=SiteCollection.Types.ADMIN,
    )
    storage = backend_collections_details.admin_site_collection_storage
    admin_sc.set_quota_limit(SiteCollection.Quotas.storage, storage)
    tenant.admin_site_collection = admin_sc

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
    storage = sum([t.quotas.get(name=SharepointTenant.Quotas.storage).limit for t in tenants])
    spl.set_quota_usage('sharepoint_storage', storage)
    spl.set_quota_usage('sharepoint_tenant_number', tenants.count())


@shared_task(name='nodeconductor.sharepoint.sync_tenants')
def sync_tenants():
    tenants = SharepointTenant.objects.filter(state=SharepointTenant.States.ONLINE)
    for tenant in tenants:
        sync_site_collection_quotas.delay([tenant.uuid])


@shared_task(name='nodeconductor.sharepoint.sync_site_collection_quotas')
def sync_site_collection_quotas(tenant_uuids):
    """Sync site collection quotas of one or more tenants"""

    if not isinstance(tenant_uuids, (list, tuple)):
        tenant_uuids = [tenant_uuids]

    tenants = SharepointTenant.objects.filter(uuid__in=tenant_uuids)

    for tenant in tenants:
        backend = tenant.get_backend()
        site_collections_data = backend.site_collections.list()
        for sc in site_collections_data:
            registered_site_collection = SiteCollection.objects.filter(access_url=sc.url).first()
            if registered_site_collection:
                registered_site_collection.set_quota_usage(SiteCollection.Quotas.storage, sc.storage_usage)
                registered_site_collection.set_quota_limit(SiteCollection.Quotas.storage, sc.storage_limit)

