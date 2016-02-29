from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices
from nodeconductor.template import TemplateRegistry


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.sharepoint'
    verbose_name = 'SaltStack SharePoint'
    service_name = 'SaltStack'

    def ready(self):
        from .cost_tracking import SaltStackCostTrackingBackend
        CostTrackingRegister.register(self.label, SaltStackCostTrackingBackend)

        # template
        from .template import SharepointTenantTemplateForm
        TemplateRegistry.register(SharepointTenantTemplateForm)

        from .backend import SharepointBackend
        SupportedServices.register_backend(SharepointBackend, nested=True)
