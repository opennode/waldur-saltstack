from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from ..saltstack.backend import SaltStackBackendError
from .backend import ExchangeBackend
from .models import Tenant


class Type(object):
    CONTACTS = 'contacts'
    GROUPS = 'groups'
    USERS = 'users'
    STORAGE = 'storage'

    CHOICES = {
        CONTACTS: 'count',
        GROUPS: 'count',
        USERS: 'count',
        STORAGE: '1 GB',
    }


class SaltStackCostTrackingBackend(CostTrackingBackend):

    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(Tenant)
        for item, key in Type.CHOICES.iteritems():
            yield DefaultPriceListItem(item_type=item, key=key, resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, tenant):
        backend = tenant.get_backend()
        users = backend.users.list()

        def get_mailboxes_usage(users):
            for user in users:
                try:
                    stats = backend.users.stats(id=user.id)
                    yield stats.usage
                except SaltStackBackendError:
                    continue

        items = {
            Type.CONTACTS: len(backend.contacts.list()),
            Type.GROUPS: len(backend.groups.list()),
            Type.USERS: len(users),
            Type.STORAGE: ExchangeBackend.mb2gb(sum(get_mailboxes_usage(users))),
        }

        return [(item, key, items[item]) for item, key in Type.CHOICES.iteritems()]
