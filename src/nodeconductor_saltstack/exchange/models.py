from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils import FieldTracker

from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.quotas.fields import QuotaField, CounterQuotaField
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink, SaltStackProperty
from .validators import domain_validator, username_validator


class ExchangeTenant(QuotaModelMixin, structure_models.Resource, structure_models.PaidResource):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='exchange_tenants', on_delete=models.PROTECT)

    domain = models.CharField(max_length=255, validators=[domain_validator])
    max_users = models.PositiveSmallIntegerField(help_text='Maximum number of mailboxes')
    mailbox_size = models.PositiveSmallIntegerField(help_text='Maximum size of single mailbox, MB')

    class Quotas(QuotaModelMixin.Quotas):
        user_count = CounterQuotaField(
            target_models=lambda: [User],
            path_to_scope='tenant',
            default_limit=lambda scope: scope.max_users,
        )
        global_mailbox_size = QuotaField(
            default_limit=lambda scope: scope.mailbox_size * scope.max_users
        )

    @classmethod
    def get_url_name(cls):
        return 'exchange-tenants'

    def get_backend(self):
        from .backend import ExchangeBackend
        return super(ExchangeTenant, self).get_backend(backend_class=ExchangeBackend, tenant=self)

    def is_username_available(self, username):
        for model in (User, Group):
            if username in model.objects.filter(tenant=self).values_list('username', flat=True):
                return False
        return True


class ExchangeProperty(SaltStackProperty):
    tenant = models.ForeignKey(ExchangeTenant, related_name='+')

    class Meta(object):
        abstract = True


@python_2_unicode_compatible
class User(ExchangeProperty):
    username = models.CharField(max_length=255, validators=[username_validator])
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    mailbox_size = models.PositiveSmallIntegerField(help_text='Maximum size of mailbox, MB')
    office = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey('User', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)

    tracker = FieldTracker()

    class Meta(object):
        unique_together = (('username', 'tenant'), ('name', 'tenant'))

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)

    def get_stats(self):
        backend = self.tenant.get_backend()
        return backend.users.stats(id=self.backend_id)

    def __str__(self):
        return '%s (%s)' % (self.name, self.tenant)


class Contact(ExchangeProperty):
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Group(ExchangeProperty):
    manager = models.ForeignKey(User, related_name='groups')
    username = models.CharField(max_length=255)
    members = models.ManyToManyField(User)

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)
