from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from nodeconductor.core import models as core_models
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models


class SaltStackService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='saltstack_services', through='SaltStackServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'saltstack'


class SaltStackServiceProjectLink(QuotaModelMixin, structure_models.ServiceProjectLink):
    service = models.ForeignKey(SaltStackService)

    class Meta(object):
        verbose_name = 'SaltStack service project link'
        verbose_name_plural = 'SaltStack service project links'

    DEFAULT_EXCHANGE_STORAGE_LIMIT = 50 * 1024  # 50 GB
    QUOTAS_NAMES = [
        'exchange_storage'
    ]

    @classmethod
    def get_url_name(cls):
        return 'saltstack-spl'


@python_2_unicode_compatible
class SaltStackProperty(core_models.UuidMixin, core_models.NameMixin, models.Model):
    backend_id = models.CharField(max_length=255, db_index=True)

    class Meta(object):
        abstract = True

    def __str__(self):
        return self.name
