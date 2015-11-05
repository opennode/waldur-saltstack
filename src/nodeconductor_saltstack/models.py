from django.db import models

from nodeconductor.billing.models import PaidResource
from nodeconductor.cost_tracking import CostConstants
from nodeconductor.structure import ServiceBackend, models as structure_models


class SaltStackService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='saltstack_services', through='SaltStackServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'saltstack'


class SaltStackServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(SaltStackService)

    exchange_target = models.CharField(
        max_length=255, help_text='Salt minion target with MS Exchange Domains')
    sharepoint_target = models.CharField(
        max_length=255, help_text='Salt minion target with MS Sharepoint Sites')

    @classmethod
    def get_url_name(cls):
        return 'saltstack-spl'


class Domain(PaidResource, structure_models.Resource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='domains', on_delete=models.PROTECT)

    def get_usage_state(self):
        return {
            CostConstants.PriceItem.USERS: 0,                          # XXX: get users count from backend
            CostConstants.PriceItem.STORAGE: ServiceBackend.mb2gb(0),  # XXX: get storage size from backend
        }

    @classmethod
    def get_url_name(cls):
        return 'saltstack-domains'

    def get_backend(self):
        return super(Domain, self).get_backend(target=self.service_project_link.exchange_target)


class Site(PaidResource, structure_models.Resource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sites', on_delete=models.PROTECT)

    def get_usage_state(self):
        return {
            CostConstants.PriceItem.USAGE: 1,
            CostConstants.PriceItem.STORAGE: ServiceBackend.mb2gb(0),  # XXX: get storage size from backend
        }

    @classmethod
    def get_url_name(cls):
        return 'saltstack-sites'

    def get_backend(self):
        return super(Site, self).get_backend(target=self.service_project_link.sharepoint_target)
