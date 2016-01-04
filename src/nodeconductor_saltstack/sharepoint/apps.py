from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.template import TemplateRegistry


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.sharepoint'
    verbose_name = "NodeConductor SaltStack SharePoint"
    service_name = 'SaltStack'

    def ready(self):
        from .cost_tracking import SaltStackCostTrackingBackend
        CostTrackingRegister.register(self.label, SaltStackCostTrackingBackend)

        # template
        from .template import SiteProvisionTemplateForm
        TemplateRegistry.register(SiteProvisionTemplateForm)

        # import it here in order to register as SaltStack backend
        from .backend import SharepointBackend

        from . import handlers
        from ..saltstack.models import SaltStackServiceProjectLink
        signals.post_save.connect(
            handlers.init_sharepoint_storage_limit,
            sender=SaltStackServiceProjectLink,
            dispatch_uid='nodeconductor_saltstack.sharepoint.handlers.init_sharepoint_storage_limit',
        )
