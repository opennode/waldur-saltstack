from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.sharepoint'
    verbose_name = "NodeConductor SaltStack SharePoint"

    def ready(self):
        from .cost_tracking import SaltStackCostTrackingBackend
        CostTrackingRegister.register(self.label, SaltStackCostTrackingBackend)
