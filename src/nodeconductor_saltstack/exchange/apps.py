from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.template import TemplateRegistry


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.exchange'
    verbose_name = "NodeConductor SaltStack Exchange"
    service_name = 'SaltStack'

    def ready(self):
        from .cost_tracking import SaltStackCostTrackingBackend
        CostTrackingRegister.register(self.label, SaltStackCostTrackingBackend)

        # template
        from .template import TenantProvisionTemplateForm
        TemplateRegistry.register(TenantProvisionTemplateForm)

        # import it here in order to register as SaltStack backend
        from .backend import ExchangeBackend

        from . import handlers
        ExchangeTenant = self.get_model('ExchangeTenant')
        User = self.get_model('User')
        ConferenceRoom = self.get_model('ConferenceRoom')

        # Tenants CRUD
        signals.post_save.connect(
            handlers.increase_exchange_storage_usage_on_tenant_creation,
            sender=ExchangeTenant,
            dispatch_uid='nodeconductor.saltstack.exchange.handlers.increase_exchange_storage_usage_on_tenant_creation',
        )

        signals.post_delete.connect(
            handlers.decrease_exchange_storage_usage_on_tenant_deletion,
            sender=ExchangeTenant,
            dispatch_uid='nodeconductor.saltstack.exchange.handlers.decrease_exchange_storage_usage_on_tenant_deletion',
        )

        # Users CRUD
        signals.post_save.connect(
            handlers.increase_global_mailbox_size_usage_on_user_creation_or_modification,
            sender=User,
            dispatch_uid=('nodeconductor.saltstack.exchange.handlers'
                          '.increase_global_mailbox_size_usage_on_user_creation_or_modification'),
        )

        signals.post_delete.connect(
            handlers.decrease_global_mailbox_size_usage_on_user_deletion,
            sender=User,
            dispatch_uid='nodeconductor.saltstack.exchange.handlers.decrease_global_mailbox_size_usage_on_user_deletion',
        )

        # Conference rooms CRUD
        signals.post_save.connect(
            handlers.increase_global_mailbox_size_usage_on_conference_room_creation_or_modification,
            sender=ConferenceRoom,
            dispatch_uid=('nodeconductor.saltstack.exchange.handlers'
                          '.increase_global_mailbox_size_usage_on_conference_room_creation_or_modification'),
        )

        signals.post_delete.connect(
            handlers.decrease_global_mailbox_size_usage_on_conference_room_deletion,
            sender=ConferenceRoom,
            dispatch_uid=('nodeconductor.saltstack.exchange.handlers'
                          '.decrease_global_mailbox_size_usage_on_conference_room_deletion'),
        )
