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
        from .template import SharepointTenantTemplateForm
        TemplateRegistry.register(SharepointTenantTemplateForm)

        # import it here in order to register as SaltStack backend
        from .backend import SharepointBackend

        from . import handlers
        SharepointTenant = self.get_model('SharepointTenant')
        User = self.get_model('User')
        SiteCollection = self.get_model('SiteCollection')

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

        # TODO: Redo this signals
        # signals.post_save.connect(
        #     handlers.update_tenant_storage_size_quotas_on_user_update,
        #     sender=User,
        #     dispatch_uid='nodeconductor.saltstack.sharepoint.handlers.update_tenant_storage_size_quotas_on_user_save',
        # )

        # signals.post_delete.connect(
        #     handlers.update_tenant_storage_size_quotas_on_user_update,
        #     sender=User,
        #     dispatch_uid='nodeconductor.saltstack.sharepoint.handlers.update_tenant_storage_size_quotas_on_user_delete',
        # )

        # signals.post_save.connect(
        #     handlers.update_tenant_storage_size_quotas_on_site_update,
        #     sender=SiteCollection,
        #     dispatch_uid='nodeconductor.saltstack.sharepoint.handlers.update_tenant_storage_size_quotas_on_site_save',
        # )

        # signals.post_delete.connect(
        #     handlers.update_tenant_storage_size_quotas_on_site_update,
        #     sender=SiteCollection,
        #     dispatch_uid='nodeconductor.saltstack.sharepoint.handlers.update_tenant_storage_size_quotas_on_site_delete',
        # )
