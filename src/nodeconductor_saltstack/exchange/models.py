from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from gm2m import GM2MField
from model_utils import FieldTracker

from nodeconductor.core.models import DescendantMixin
from nodeconductor.cost_tracking.models import PayableMixin
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.quotas.fields import QuotaLimitField, QuotaField, CounterQuotaField, LimitAggregatorQuotaField
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink, SaltStackProperty
from .validators import domain_validator


class ExchangeTenant(QuotaModelMixin, structure_models.PublishableResource, structure_models.ApplicationMixin,
                     PayableMixin):
    service_project_link = models.ForeignKey(
        SaltStackServiceProjectLink, related_name='exchange_tenants', on_delete=models.PROTECT)
    domain = models.CharField(max_length=255, validators=[domain_validator])

    class Quotas(QuotaModelMixin.Quotas):
        user_count = CounterQuotaField(
            target_models=lambda: [User],
            path_to_scope='tenant',
        )
        conference_room_count = CounterQuotaField(
            target_models=lambda: [ConferenceRoom],
            path_to_scope='tenant',
        )
        # Maximum size of all mailboxes together, MB
        mailbox_size = LimitAggregatorQuotaField(
            default_limit=0,
            get_children=(lambda tenant:
                          list(User.objects.filter(tenant=tenant)) + list(ConferenceRoom.objects.filter(tenant=tenant))),
        )

    @classmethod
    def get_url_name(cls):
        return 'exchange-tenants'

    def get_backend(self):
        from .backend import ExchangeBackend
        return super(ExchangeTenant, self).get_backend(backend_class=ExchangeBackend, tenant=self)

    def is_username_available(self, username, exclude=None):
        if exclude is None:
            exclude = []
        if isinstance(exclude, basestring):
            exclude = [exclude]
        for model in (User, Group, ConferenceRoom):
            users = set(model.objects.filter(tenant=self).values_list('username', flat=True))
            if username in users - set(exclude):
                return False
        return True

    @property
    def full_name(self):
        return 'MS Exchange tenant %s' % self.name

    def get_log_fields(self):
        return super(ExchangeTenant, self).get_log_fields() + ('domain',)


class ExchangeProperty(SaltStackProperty):
    tenant = models.ForeignKey(ExchangeTenant, related_name='+')

    class Meta(object):
        abstract = True

    def get_log_fields(self):
        return super(ExchangeProperty, self).get_log_fields() + ('tenant',)


class MailboxExchangeProperty(QuotaModelMixin, DescendantMixin, ExchangeProperty):

    class Meta(object):
        abstract = True

    class Quotas(QuotaModelMixin.Quotas):
        # Size of one mailbox, MB
        mailbox_size = QuotaField(default_limit=0, is_backend=True)

    mailbox_size = QuotaLimitField(quota_field=Quotas.mailbox_size)

    def get_parents(self):
        return [self.tenant]


@python_2_unicode_compatible
class User(MailboxExchangeProperty):
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    office = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey('User', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    send_on_behalf_members = models.ManyToManyField('self', related_name='+')
    send_as_members = models.ManyToManyField('self', related_name='+')

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

    @classmethod
    def get_url_name(cls):
        return 'exchange-users'

    def get_log_fields(self):
        return super(User, self).get_log_fields() + ('username', 'email')


class Contact(ExchangeProperty):
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    tracker = FieldTracker()

    def get_log_fields(self):
        return super(Contact, self).get_log_fields() + ('email',)


class Group(ExchangeProperty):
    manager = models.ForeignKey(User, related_name='groups')
    username = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='+')
    delivery_members = GM2MField()
    senders_out = models.BooleanField(
        default=False, help_text='Delivery management for senders outside organizational unit')

    tracker = FieldTracker()

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)

    def get_log_fields(self):
        return super(Group, self).get_log_fields() + ('username', 'email')


class ConferenceRoom(MailboxExchangeProperty):
    username = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)

    tracker = FieldTracker()

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)

    @classmethod
    def get_url_name(cls):
        return 'exchange-conference-rooms'

    def get_log_fields(self):
        return super(ConferenceRoom, self).get_log_fields() + ('username', )
