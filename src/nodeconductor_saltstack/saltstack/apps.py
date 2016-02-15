from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.saltstack'
    verbose_name = "NodeConductor SaltStack Core"
    service_name = 'SaltStack'

    def ready(self):
        from .backend import SaltStackBackend
        SupportedServices.register_backend(SaltStackBackend)

        from nodeconductor.structure.models import ServiceSettings
        from nodeconductor.quotas.fields import QuotaField

        ServiceSettings.add_quota_field(
            name='sharepoint_storage',
            quota_field=QuotaField(
                creation_condition=lambda service_settings: service_settings.type == SaltStackConfig.service_name,
            ),
        )

        ServiceSettings.add_quota_field(
            name='exchange_storage',
            quota_field=QuotaField(
                creation_condition=lambda service_settings: service_settings.type == SaltStackConfig.service_name,
            ),
        )
