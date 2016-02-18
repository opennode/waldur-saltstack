from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from nodeconductor.core import models as core_models
from nodeconductor.quotas.fields import CounterQuotaField, LimitAggregatorQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models


class SaltStackService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='saltstack_services', through='SaltStackServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'saltstack'


# to avoid circular imports
def _get_sharepoint_tenant_model():
    from ..sharepoint.models import SharepointTenant
    return [SharepointTenant]


class SaltStackServiceProjectLink(QuotaModelMixin, structure_models.ServiceProjectLink):
    service = models.ForeignKey(SaltStackService)

    class Meta(structure_models.ServiceProjectLink.Meta):
        verbose_name = 'SaltStack service project link'
        verbose_name_plural = 'SaltStack service project links'

    class Quotas(QuotaModelMixin.Quotas):
        exchange_storage = LimitAggregatorQuotaField(
            default_limit=50 * 1024,
            get_children=lambda spl: spl.exchange_tenants.all(),
            child_quota_name='mailbox_size'
        )
        sharepoint_storage = LimitAggregatorQuotaField(
            default_limit=10 * 1024,
            get_children=lambda spl: spl.sharepoint_tenants.all(),
            child_quota_name='storage',
        )
        sharepoint_tenant_number = CounterQuotaField(
            target_models=_get_sharepoint_tenant_model,
            path_to_scope='service_project_link',
            default_limit=2,
        )

    @classmethod
    def get_url_name(cls):
        return 'saltstack-spl'


@python_2_unicode_compatible
class SaltStackProperty(core_models.UuidMixin, core_models.NameMixin, models.Model):
    backend_id = models.CharField(max_length=255, db_index=True)

    class Meta(object):
        abstract = True

    def __str__(self):
        return self.name
