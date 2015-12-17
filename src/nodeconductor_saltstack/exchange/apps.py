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

        from . import handlers
        from ..saltstack.models import SaltStackServiceProjectLink
        signals.post_save.connect(
            handlers.init_exchange_storage_limit,
            sender=SaltStackServiceProjectLink,
            dispatch_uid='nodeconductor_saltstack.exchange.handlers.init_exchange_storage_limit',
        )
