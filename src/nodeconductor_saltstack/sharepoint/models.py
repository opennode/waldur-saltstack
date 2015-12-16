from django.db import models

from nodeconductor.core.models import DescribableMixin
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink


class SharepointTenant(structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sharepoint_tenants', on_delete=models.PROTECT)

    domain = models.CharField(max_length=255)
    site_name = models.CharField(max_length=255)
    site_url = models.URLField(blank=True)
    admin_url = models.URLField(blank=True)
    admin_login = models.CharField(max_length=255, blank=True)
    admin_password = models.CharField(max_length=255, blank=True)

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-tenants'

    def get_backend(self):
        from .backend import SharepointBackend
        return super(SharepointTenant, self).get_backend(backend_class=SharepointBackend, tenant=self)


class Template(structure_models.ServiceProperty):
    code = models.CharField(max_length=255)


class User(structure_models.GeneralServiceProperty):
    tenant = models.ForeignKey(SharepointTenant, related_name='users')
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    admin_id = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class Site(DescribableMixin, structure_models.GeneralServiceProperty):
    user = models.ForeignKey(User, related_name='sites')
    site_url = models.CharField(max_length=255)
