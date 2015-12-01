from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.saltstack'
    verbose_name = "NodeConductor SaltStack Core"
    service_name = 'SaltStack'

    def ready(self):
        from .backend import SaltStackBackend
        SupportedServices.register_backend(SaltStackBackend)
