from django.db import models

from nodeconductor.quotas.fields import QuotaField, CounterQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink, SaltStackProperty


class SharepointTenant(QuotaModelMixin, structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sharepoint_tenants', on_delete=models.PROTECT)

    domain = models.CharField(max_length=255)
    site_name = models.CharField(max_length=255)
    site_url = models.URLField(blank=True)
    admin_url = models.URLField(blank=True)
    admin_login = models.CharField(max_length=255, blank=True)
    admin_password = models.CharField(max_length=255, blank=True)
    storage_size = models.PositiveIntegerField(help_text='Maximum size of tenants, MB')
    user_count = models.PositiveIntegerField(help_text='Maximum number of users in tenant')

    class Quotas(QuotaModelMixin.Quotas):
        storage_size = QuotaField(
            default_limit=lambda t: t.storage_size,
            is_backend=True
        )
        user_count = CounterQuotaField(
            target_models=lambda: [User],
            path_to_scope='tenant',
            default_limit=lambda t: t.user_count,
            is_backend=True
        )

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-tenants'

    def get_backend(self):
        from .backend import SharepointBackend
        return super(SharepointTenant, self).get_backend(backend_class=SharepointBackend, tenant=self)


class Template(structure_models.ServiceProperty):
    code = models.CharField(max_length=255)

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-templates'


class SharepointProperty(SaltStackProperty):
    tenant = models.ForeignKey(SharepointTenant, related_name='+')

    class Meta(object):
        abstract = True


class User(SaltStackProperty):
    tenant = models.ForeignKey(SharepointTenant, related_name='users')
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    admin_id = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class Site(SaltStackProperty):
    user = models.ForeignKey(User, related_name='sites')
    site_url = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    # TODO: ADD max quota field and use it for tenant storage_size quota.
