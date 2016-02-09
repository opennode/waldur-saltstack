from django.db import models
from django.core.mail import send_mail
from django.utils.encoding import python_2_unicode_compatible
from model_utils import FieldTracker

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

    def is_username_available(self, username):
        for model in (User, Group):
            if username in model.objects.filter(tenant=self).values_list('username', flat=True):
                return False
        return True

    def set_quota_limit(self, quota_name, limit):
        # XXX: Increase service settings storage quota usage on tenant limit update.
        #      This type of update logic should be moved to separate quota field. Issue NC-1149.
        if str(quota_name) == self.Quotas.global_mailbox_size.name:
            old_limit = self.quotas.get(name=quota_name).limit
            if old_limit == -1:
                diff = limit
            else:
                diff = limit - old_limit
            if diff:
                service_settings = self.service_project_link.service.settings
                service_settings.add_quota_usage(service_settings.Quotas.exchange_storage, diff)
        super(ExchangeTenant, self).set_quota_limit(quota_name, limit)


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
    members = models.ManyToManyField(User)

    @property
    def email(self):
        return '{}@{}'.format(self.username, self.tenant.domain)


class ConferenceRoom(ExchangeProperty):
    alias = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    mailbox_size = models.PositiveSmallIntegerField(help_text='Maximum size of conference room mailbox, MB')
    phone = models.CharField(max_length=255, blank=True)

    @property
    def email(self):
        return '{}@{}'.format(self.alias, self.tenant.domain)
