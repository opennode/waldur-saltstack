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

        SharepointTenant = self.get_model('SharepointTenant')

        signals.post_save.connect(
            handlers.init_sharepoint_quotas,
            sender=SaltStackServiceProjectLink,
            dispatch_uid='nodeconductor_saltstack.sharepoint.handlers.init_sharepoint_quotas',
        )

        signals.post_save.connect(
            handlers.increase_quotas_usage_on_tenant_creation,
            sender=SharepointTenant,
            dispatch_uid='nodeconductor.saltstack.sharepoint.handlers.increase_quotas_usage_on_tenant_creation',
        )

        signals.post_delete.connect(
            handlers.decrease_quotas_usage_on_tenant_deletion,
            sender=SharepointTenant,
            dispatch_uid='nodeconductor.saltstack.sharepoint.handlers.decrease_quotas_usage_on_tenant_deletion',
        )
