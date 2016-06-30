from __future__ import unicode_literals

from django.db import models
from model_utils import FieldTracker

from nodeconductor.core.models import DescendantMixin
from nodeconductor.cost_tracking.models import PayableMixin
from nodeconductor.quotas.fields import QuotaField, CounterQuotaField, LimitAggregatorQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink, SaltStackProperty


class SharepointTenant(QuotaModelMixin, structure_models.PublishableResource, structure_models.ApplicationMixin,
                       PayableMixin):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sharepoint_tenants', on_delete=models.PROTECT)

    domain = models.CharField(max_length=255)

    admin = models.ForeignKey('User', related_name='+', blank=True, null=True)
    main_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)
    admin_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)

    class Quotas(QuotaModelMixin.Quotas):
        storage = LimitAggregatorQuotaField(
            get_children=lambda tenant: SiteCollection.objects.filter(user__tenant=tenant)
        )
        user_count = CounterQuotaField(
            target_models=lambda: [User],
            path_to_scope='tenant',
        )

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-tenants'

    def get_backend(self):
        from .backend import SharepointBackend
        return super(SharepointTenant, self).get_backend(backend_class=SharepointBackend, tenant=self)

    def get_default_site_collections(self):
        return [self.main_site_collection, self.admin_site_collection]

    def get_access_url(self):
        if self.main_site_collection:
            return self.main_site_collection.access_url
        return

    @property
    def full_name(self):
        return 'MS SharePoint tenant %s' % self.name

    def get_log_fields(self):
        return ('uuid', 'name', 'domain', 'service_project_link')


class Template(structure_models.ServiceProperty):
    code = models.CharField(max_length=255)

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-templates'


class User(SaltStackProperty):
    tenant = models.ForeignKey(SharepointTenant, related_name='users')
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    admin_id = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True)
    personal_site_collection = models.ForeignKey('SiteCollection', related_name='+', blank=True, null=True)

    tracker = FieldTracker()

    class Defaults(object):
        admin = {
            'name': 'Admin',
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'Admin',
        }

    def init_personal_site_collection(self, url):
        self.personal_site_collection = SiteCollection.objects.create(
            name=SiteCollection.Defaults.personal_site_collection['name'],
            description=SiteCollection.Defaults.personal_site_collection['description'],
            type=SiteCollection.Types.PERSONAL,
            user=self,
            access_url=url,
        )
        default_storage = SiteCollection.Defaults.personal_site_collection['storage']
        self.personal_site_collection.set_quota_limit(SiteCollection.Quotas.storage, default_storage)
        self.save()

    def get_log_fields(self):
        return super(User, self).get_log_fields() + ('tenant', 'email')


class SiteCollection(QuotaModelMixin, SaltStackProperty, DescendantMixin):

    class Types(object):
        MAIN = 'main'
        ADMIN = 'admin'
        PERSONAL = 'personal'
        REGULAR = 'regular'

        CHOICES = ((MAIN, MAIN), (ADMIN, ADMIN), (PERSONAL, PERSONAL), (REGULAR, REGULAR))

    type = models.CharField(max_length=30, choices=Types.CHOICES, default=Types.REGULAR)
    user = models.ForeignKey(User, related_name='site_collections')
    site_url = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=500)
    template = models.ForeignKey(Template, related_name='site_collections', blank=True, null=True)
    access_url = models.CharField(max_length=255)

    tracker = FieldTracker()

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-site-collections'

    class Quotas(QuotaModelMixin.Quotas):
        storage = QuotaField(default_limit=0)

    class Defaults(object):
        """ Default parameters for initial tenant site collections """
        personal_site_collection = {
            'name': 'Personal',
            'description': 'Personal site collection',
            'storage': 5,  # storage per user
        }
        admin_site_collection = {
            'name': 'Admin',
            'description': 'Admin site collection',
            'storage': 50,
        }
        main_site_collection = {
            'storage': 500,
        }

    @property
    def deletable(self):
        return self.type == self.Types.REGULAR

    def get_parents(self):
        return [self.user.tenant]

    def get_log_fields(self):
        return super(SiteCollection, self).get_log_fields() + ('user',)
