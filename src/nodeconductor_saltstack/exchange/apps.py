from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.exchange'
    verbose_name = 'SaltStack Exchange'
    service_name = 'SaltStack'

    def ready(self):
        from .backend import ExchangeBackend
        SupportedServices.register_backend(ExchangeBackend, nested=True)
