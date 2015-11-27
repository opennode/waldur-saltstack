from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.exchange'
    verbose_name = "NodeConductor SaltStack Exchange"

    def ready(self):
        from .cost_tracking import SaltStackCostTrackingBackend
        CostTrackingRegister.register(self.label, SaltStackCostTrackingBackend)
