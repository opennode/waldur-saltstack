from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.sharepoint'
    verbose_name = 'SaltStack SharePoint'
    service_name = 'SaltStack'

    def ready(self):
        from .backend import SharepointBackend
        SupportedServices.register_backend(SharepointBackend, nested=True)
