from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack'
    verbose_name = "NodeConductor SaltStack"
    service_name = 'SaltStack'

    def ready(self):
        from .backend import SaltStackBackend
        from .cost_tracking import SaltStackCostTrackingBackend
        SupportedServices.register_backend(SaltStackBackend)
        CostTrackingRegister.register(self.label, SaltStackCostTrackingBackend)
