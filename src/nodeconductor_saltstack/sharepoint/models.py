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
        max_length=20, choices=InitializationStatuses.CHOICES, default=InitializationStatuses.NOT_INITIALIZED)

    main_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)
    admin_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)
    users_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)

    class Quotas(QuotaModelMixin.Quotas):
        storage = QuotaField(
            default_limit=5 * 1024,
        )
        user_count = CounterQuotaField(
            target_models=lambda: [User],
            path_to_scope='tenant',
            default_limit=10,
        )

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-tenants'

    def get_backend(self):
        from .backend import SharepointBackend
        return super(SharepointTenant, self).get_backend(backend_class=SharepointBackend, tenant=self)

    def initialize(self, main_site_collection, admin_site_collection, users_site_collection):
        self.main_site_collection = main_site_collection
        self.admin_site_collection = admin_site_collection
        self.users_site_collection = users_site_collection
        self.initialization_status = self.InitializationStatuses.INITIALIZED
        self.save()


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
    site_url = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    template = models.ForeignKey(Template, related_name='site_collections')
    access_url = models.CharField(max_length=255, blank=True)

    class Quotas(QuotaModelMixin.Quotas):
        storage = QuotaField(is_backend=True)

    # TODO: ADD max quota field and use it for tenant storage_size quota.
