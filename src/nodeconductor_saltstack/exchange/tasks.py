from celery import shared_task, chain
from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition, throttle
from nodeconductor.structure.tasks import sync_service_project_links

from ..saltstack.utils import sms_user_password
from .models import ExchangeTenant, ConferenceRoom, User


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

        user = User.objects.create(
            tenant=tenant,
            backend_id=backend_user.id,
            password=backend_user.password,
            **kwargs)
        if notify:
            sms_user_password(user)


@shared_task
@transition(ExchangeTenant, 'begin_deleting')
@save_error_message
def destroy_tenant(tenant_uuid, transition_entity=None):
    tenant = ExchangeTenant.objects.get(uuid=tenant_uuid)
    backend = tenant.get_backend()
    backend.tenants.delete()


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


@shared_task(name='nodeconductor.exchange.sync_tenants')
def sync_tenants():
    tenants = ExchangeTenant.objects.filter(state=ExchangeTenant.States.ONLINE)
    for tenant in tenants:
        sync_tenant_quotas.delay(tenant.uuid.hex)


@shared_task
def sync_tenant_quotas(tenant_uuids):
    if not isinstance(tenant_uuids, (list, tuple)):
        tenant_uuids = [tenant_uuids]

    tenants = ExchangeTenant.objects.filter(uuid__in=tenant_uuids)
    stats = {User: {}, ConferenceRoom: {}}

    for tenant in tenants:
        backend = tenant.get_backend()
        counts = {User: 0, ConferenceRoom: 0}
        for data in backend.stats.mailbox():
            if data.type == 'UserMailbox':
                stats[User][data.user_id] = data
                counts[User] += 1
            elif data.type == 'RoomMailbox':
                stats[ConferenceRoom][data.user_id] = data
                counts[ConferenceRoom] += 1

        tenant.set_quota_usage(ExchangeTenant.Quotas.user_count, counts[User])
        tenant.set_quota_usage(ExchangeTenant.Quotas.conference_room_count, counts[ConferenceRoom])

    for model in (User, ConferenceRoom):
        for obj in model.objects.filter(backend_id__in=stats[model].keys()):
            data = stats[model][obj.backend_id]
            obj.set_quota_usage(model.Quotas.mailbox_size, data.usage)
            obj.set_quota_limit(model.Quotas.mailbox_size, data.limit)
