from django.db import models

from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink


class ExchangeResource(structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='+', on_delete=models.PROTECT)

    def get_backend(self):
        from .backend import ExchangeBackend
        return super(ExchangeResource, self).get_backend(backend_class=ExchangeBackend)

    class Meta:
        abstract = True


class Tenant(ExchangeResource):
    domain = models.CharField(max_length=255)

    @classmethod
    def get_url_name(cls):
        return 'saltstack-tenants'


class DistributionGroup(ExchangeResource):
    tenant = models.ForeignKey(Tenant, related_name='users')
    email = models.EmailField(unique=True)

    @classmethod
    def get_url_name(cls):
        return 'saltstack-distgroup-users'
