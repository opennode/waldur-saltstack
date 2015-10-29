from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack'
    verbose_name = "NodeConductor SaltStack"

    def ready(self):
        SaltStackService = self.get_model('SaltStackService')

        from .backend import SaltStackBackend
        SupportedServices.register_backend(SaltStackService, SaltStackBackend)
