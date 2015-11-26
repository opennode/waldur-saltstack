from django.db import models

from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink


class Tenant(structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='tenants', on_delete=models.PROTECT)

    domain = models.CharField(max_length=255)
    max_users = models.PositiveSmallIntegerField(help_text='Maximum number of mailboxes')
    mailbox_size = models.PositiveSmallIntegerField(help_text='Maximum size of single mailbox, GB')

    @classmethod
    def get_url_name(cls):
        return 'exchange-tenants'

    def get_backend(self):
        from .backend import ExchangeBackend
        return super(Tenant, self).get_backend(backend_class=ExchangeBackend, tenant=self)
