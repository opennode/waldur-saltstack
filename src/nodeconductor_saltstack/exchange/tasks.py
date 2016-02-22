from celery import shared_task, chain
from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition, throttle
from nodeconductor.structure.tasks import sync_service_project_links

from ..saltstack.utils import sms_user_password
from .models import ExchangeTenant, User


@shared_task(name='nodeconductor.exchange.provision')
def provision(tenant_uuid, **kwargs):
    tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
    chain(
        sync_service_project_links.s(tenant.service_project_link.to_string(), initial=True),
        provision_tenant.si(tenant_uuid, **kwargs),
    ).apply_async(
        link=set_online.si(tenant_uuid),
        link_error=set_erred.si(tenant_uuid))


@shared_task(name='nodeconductor.exchange.destroy')
@transition(ExchangeTenant, 'schedule_deletion')
def destroy(tenant_uuid, force=False, transition_entity=None):
    error_callback = delete.si(tenant_uuid) if force else set_erred.si(tenant_uuid)
    destroy_tenant.apply_async(
        args=(tenant_uuid,),
        link=delete.si(tenant_uuid),
        link_error=error_callback,
    )


@shared_task(name='nodeconductor.exchange.create_user')
def create_user(tenant_uuid, notify=False, **kwargs):
    tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
    with throttle(key=tenant.service_project_link.service.settings.backend_url, concurrency=3):
        backend = tenant.get_backend()
        backend_user = backend.users.create(**kwargs)

        user = User.objects.create(tenant=tenant, backend_id=backend_user.id, **kwargs)
        if notify:
            sms_user_password(user)


@shared_task
@transition(ExchangeTenant, 'begin_deleting')
@save_error_message
def destroy_tenant(tenant_uuid, transition_entity=None):
    tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
    backend = tenant.get_backend()
    backend.tenants.delete()
    event_logger.exchange_tenant.info(
        'Tenant {tenant_name} has been created.',
        event_type='exchange_tenant_creation_succeeded',
        event_context={
            'tenant': tenant
        }
    )



@shared_task(is_heavy_task=True)
@transition(ExchangeTenant, 'begin_provisioning')
@save_error_message
def provision_tenant(tenant_uuid, transition_entity=None, **kwargs):
    tenant = transition_entity
    backend = tenant.get_backend()
    backent_tenant = backend.tenants.create(mailbox_size=kwargs['mailbox_size'])

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
def delete(tenant_uuid):
    ExchangeTenant.objects.get(uuid=tenant_uuid).delete()


# TODO: rewrite sync methods

# @shared_task
# def sync_tenant_quotas(tenant_uuid):
#     tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
#     users = list(User.objects.filter(tenant=tenant))
#     tenant.set_quota_usage('user_count', len(users))
#     tenant.set_quota_usage('mailbox_size', sum(user.mailbox_size for user in users))


# @shared_task
# def sync_spl_quotas(spl_id):
#     spl = SaltStackServiceProjectLink.objects.get(id=spl_id)
#     tenants = ExchangeTenant.objects.filter(service_project_link=spl)
#     spl.set_quota_usage('exchange_storage', sum([t.max_users * t.mailbox_size for t in tenants]))
