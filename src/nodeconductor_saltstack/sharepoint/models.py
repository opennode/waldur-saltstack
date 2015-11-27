from django.db import models

from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink


class Site(structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='sites', on_delete=models.PROTECT)

    @classmethod
    def get_url_name(cls):
        return 'sharepoint-sites'

    def get_backend(self):
        from .backend import SharepointBackend
        return super(Site, self).get_backend(backend_class=SharepointBackend)
