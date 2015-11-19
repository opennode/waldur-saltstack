from django.db import models

from nodeconductor.structure import models as structure_models


class SaltStackService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='saltstack_services', through='SaltStackServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'saltstack'


class SaltStackServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(SaltStackService)

    @classmethod
    def get_url_name(cls):
        return 'saltstack-spl'


class Domain(structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='domains', on_delete=models.PROTECT)

    @classmethod
    def get_url_name(cls):
        return 'saltstack-domains'


class Site(structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sites', on_delete=models.PROTECT)

    @classmethod
    def get_url_name(cls):
        return 'saltstack-sites'
