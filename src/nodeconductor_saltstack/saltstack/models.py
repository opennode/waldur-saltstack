from __future__ import unicode_literals

from django.apps import apps
from django.db import models
from django.utils.lru_cache import lru_cache
from django.utils.encoding import python_2_unicode_compatible
from model_utils import FieldTracker

from nodeconductor.core import models as core_models
from nodeconductor.logging.loggers import LoggableMixin
from nodeconductor.quotas.fields import CounterQuotaField, LimitAggregatorQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models


class SaltStackService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='saltstack_services', through='SaltStackServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'saltstack'

    class Meta(structure_models.Service.Meta):
        verbose_name = 'SaltStack service'
        verbose_name_plural = 'SaltStack service'


# to avoid circular imports
def _get_sharepoint_tenant_model():
    from ..sharepoint.models import SharepointTenant
    return [SharepointTenant]


def _get_exchange_tenant_model():
    from ..exchange.models import ExchangeTenant
    return [ExchangeTenant]


def _get_site_collection_model():
    from ..sharepoint.models import SiteCollection
    return [SiteCollection]


def _get_mailbox_models():
    from ..exchange.models import User, ConferenceRoom
    return [User, ConferenceRoom]


class SaltStackServiceProjectLink(structure_models.ServiceProjectLink):
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
            default_limit=-1,
        )
        exchange_tenant_number = CounterQuotaField(
            target_models=_get_exchange_tenant_model,
            path_to_scope='service_project_link',
            default_limit=-1,
        )
        site_collection_count = CounterQuotaField(
            target_models=_get_site_collection_model,
            path_to_scope='user.tenant.service_project_link',
            default_limit=-1,
        )
        mailbox_count = CounterQuotaField(
            target_models=_get_mailbox_models,
            path_to_scope='tenant.service_project_link',
            default_limit=-1,
        )

    @classmethod
    def get_url_name(cls):
        return 'saltstack-spl'


@python_2_unicode_compatible
class SaltStackProperty(core_models.UuidMixin, core_models.NameMixin, LoggableMixin, models.Model):
    backend_id = models.CharField(max_length=255, db_index=True)

    tracker = FieldTracker()

    class Meta(object):
        abstract = True

    def __str__(self):
        return self.name

    @classmethod
    def get_type_name(cls):
        return '%s.%s' % (cls._meta.app_label, cls._meta.model_name)

    @classmethod
    def get_type_display_name(cls):
        return '%s %s' % (cls._meta.app_label.title(), cls._meta.verbose_name)

    def _get_log_context(self, entity_name):
        context = super(SaltStackProperty, self)._get_log_context(entity_name)
        context['property_type'] = self.get_type_name()
        return context

    @classmethod
    @lru_cache(maxsize=1)
    def get_all_models(cls):
        return [model for model in apps.get_models() if issubclass(model, cls)]
