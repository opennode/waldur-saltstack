from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from ..saltstack.backend import SaltStackBackendError
from .backend import ExchangeBackend
from .models import ExchangeTenant, Contact, Group, User


class Type(object):
    CONTACTS = 'contacts'
    GROUPS = 'groups'
    USERS = 'users'
    STORAGE = 'storage'

    CHOICES = {
        CONTACTS: 'count',
        GROUPS: 'count',
        USERS: 'count',
        STORAGE: '1 MB',
    }


class SaltStackCostTrackingBackend(CostTrackingBackend):

    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(ExchangeTenant)
        for item, key in Type.CHOICES.iteritems():
            yield DefaultPriceListItem(item_type=item, key=key, resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, tenant):

        def get_mailboxes_usage(users):
            for user in users:
                try:
                    stats = user.get_stats()
                    yield stats.usage
                except SaltStackBackendError:
                    continue

        users = list(User.objects.filter(tenant=tenant))
        items = {
            Type.CONTACTS: Contact.objects.filter(tenant=tenant).count(),
            Type.GROUPS: Group.objects.filter(tenant=tenant).count(),
            Type.USERS: len(users),
            Type.STORAGE: ExchangeBackend.mb2gb(sum(get_mailboxes_usage(users))),
        }

        return [(item, key, items[item]) for item, key in Type.CHOICES.iteritems()]
