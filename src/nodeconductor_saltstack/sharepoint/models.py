from django.db import models

from nodeconductor.quotas.fields import QuotaField, CounterQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink, SaltStackProperty


class SharepointTenant(QuotaModelMixin, structure_models.Resource, structure_models.PaidResource):
    class InitializationStatuses(object):
        NOT_INITIALIZED = 'Not initialized'
        INITIALIZING = 'Initializing'
        INITIALIZED = 'Initialized'
        FAILED = 'Initialization failed'

        CHOICES = ((NOT_INITIALIZED, NOT_INITIALIZED), (INITIALIZING, INITIALIZING),
                   (INITIALIZED, INITIALIZED), (FAILED, FAILED))

    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sharepoint_tenants', on_delete=models.PROTECT)

    domain = models.CharField(max_length=255)
    initialization_status = models.CharField(
        max_length=30, choices=InitializationStatuses.CHOICES, default=InitializationStatuses.NOT_INITIALIZED)

    main_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)
    admin_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)
    personal_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)

    class Quotas(QuotaModelMixin.Quotas):
        storage = QuotaField(
            default_limit=0,
        )
        user_count = CounterQuotaField(
            target_models=lambda: [User],
            path_to_scope='tenant',
            default_limit=0,
        )

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-tenants'

    def get_backend(self):
        from .backend import SharepointBackend
        return super(SharepointTenant, self).get_backend(backend_class=SharepointBackend, tenant=self)

    def get_default_site_collections(self):
        return [self.main_site_collection, self.admin_site_collection, self.personal_site_collection]

    def get_access_url(self):
        if self.main_site_collection:
            return self.main_site_collection.access_url

    def set_quota_limit(self, quota_name, limit):
        # XXX: Increase service settings storage quota usage on tenant limit update.
        #      This type of update logic should be moved to separate quota field. Issue NC-1149.
        if str(quota_name) == self.Quotas.storage.name:
            old_limit = self.quotas.get(name=quota_name).limit
            if old_limit == -1:
                diff = limit
            else:
                diff = limit - old_limit
            if diff:
                service_settings = self.service_project_link.service.settings
                service_settings.add_quota_usage(service_settings.Quotas.sharepoint_storage, diff)
        super(SharepointTenant, self).set_quota_limit(quota_name, limit)


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


class SiteCollection(QuotaModelMixin, SaltStackProperty):
    user = models.ForeignKey(User, related_name='site_collections')
    site_url = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=500)
    template = models.ForeignKey(Template, related_name='site_collections', blank=True, null=True)
    access_url = models.CharField(max_length=255)

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-site-collections'

    class Quotas(QuotaModelMixin.Quotas):
        storage = QuotaField()

    class Defaults(object):
        """ Default parameters for initial tenant site collections """
        personal_site_collection = {
            'name': 'Personal',
            'description': 'Personal site collection',
            'storage': 100,  # storage per user
        }
        admin_site_collection = {
            'name': 'Admin',
            'description': 'Admin site collection',
            'storage': 100,
        }

    @property
    def deletable(self):
        return self not in self.user.tenant.get_default_site_collections()
