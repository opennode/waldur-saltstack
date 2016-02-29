from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.structure import SupportedServices


class SaltStackConfig(AppConfig):
    name = 'nodeconductor_saltstack.saltstack'
    verbose_name = 'SaltStack Core'
    service_name = 'SaltStack'

    def ready(self):
        from .backend import SaltStackBackend
        from .models import SaltStackProperty
        import handlers
        SupportedServices.register_backend(SaltStackBackend)

        from nodeconductor.structure.models import ServiceSettings
        from nodeconductor.quotas.fields import QuotaField, CounterQuotaField
        from ..exchange.models import ExchangeTenant

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

        ServiceSettings.add_quota_field(
            name='exchange_tenant_count',
            quota_field=CounterQuotaField(
                creation_condition=lambda service_settings: service_settings.type == SaltStackConfig.service_name,
                target_models=[ExchangeTenant],
                path_to_scope='service_project_link.service.settings',
            )
        )

        for index, model in enumerate(SaltStackProperty.get_all_models()):
            signals.post_save.connect(
                handlers.log_saltstack_property_created,
                sender=model,
                dispatch_uid='nodeconductor_saltstack.saltstack.handlers.log_saltstack_property_created{}_{}'.format(
                    model.__name__, index),
            )

            signals.post_delete.connect(
                handlers.log_saltstack_property_deleted,
                sender=model,
                dispatch_uid='nodeconductor_saltstack.saltstack.handlers.log_saltstack_property_deleted{}_{}'.format(
                    model.__name__, index),
            )
