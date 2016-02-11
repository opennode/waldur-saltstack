from django.db import models
from django.core.mail import send_mail
from django.utils.encoding import python_2_unicode_compatible
from model_utils import FieldTracker
from gm2m import GM2MField

from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.quotas.fields import QuotaField, CounterQuotaField
from nodeconductor.structure import models as structure_models

from ..saltstack.models import SaltStackServiceProjectLink, SaltStackProperty
from .validators import domain_validator


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


class ExchangeProperty(SaltStackProperty):
    tenant = models.ForeignKey(ExchangeTenant, related_name='+')

    class Meta(object):
        abstract = True


@python_2_unicode_compatible
class User(ExchangeProperty):
    username = models.CharField(max_length=255)
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

    def notify(self):
        if self.phone:
            options = self.tenant.service_project_link.service.settings.options or {}
            sender = options.get('sms_email_from')
            recipient = options.get('sms_email_rcpt')

            if sender and recipient and '{phone}' in recipient:
                send_mail(
                    '', self.password, sender,
                    [recipient.format(phone=self.phone)], fail_silently=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.tenant)


class Contact(ExchangeProperty):
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Group(ExchangeProperty):
    manager = models.ForeignKey(User, related_name='groups')
    username = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='+')
    delivery_members = GM2MField()
    senders_out = models.BooleanField(
        default=False, help_text='Delivery management for senders outside organizational unit')

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)


class ConferenceRoom(ExchangeProperty):
    username = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    mailbox_size = models.PositiveSmallIntegerField(help_text='Maximum size of conference room mailbox, MB')

    tracker = FieldTracker()

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)
