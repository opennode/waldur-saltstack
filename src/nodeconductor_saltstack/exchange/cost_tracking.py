from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from .backend import ExchangeBackend
from .models import Tenant


class Type(object):
    CONTACTS = 'contacts'
    DISTGROUPS = 'distgroups'
    USERS = 'users'
    STORAGE = 'storage'

    CONTACTS_KEY = 'count'
    DISTGROUPS_KEY = 'count'
    STORAGE_KEY = '1 GB'
    USERS_KEY = 'count'

    CHOICES = {
        CONTACTS: CONTACTS_KEY,
        DISTGROUPS: DISTGROUPS_KEY,
        USERS: USERS_KEY,
        STORAGE: STORAGE_KEY,
    }


class SaltStackCostTrackingBackend(CostTrackingBackend):
    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(Tenant)
        for item, key in Type.CHOICES.iteritems():
            yield DefaultPriceListItem(item_type=item, key=key, resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, tenant):
        api = tenant.get_backend().api
        users = api.list_users(tenant.name)
        storage = sum(user['mailbox_size'] for user in users)
        return [
            (Type.CONTACTS, Type.CHOICES[Type.CONTACTS], len(api.list_contacts(tenant.name))),
            (Type.DISTGROUPS, Type.CHOICES[Type.DISTGROUPS], len(api.list_distgroups(tenant.name))),
            (Type.USERS, Type.CHOICES[Type.USERS], len(users)),
            (Type.STORAGE, Type.CHOICES[Type.STORAGE], ExchangeBackend.mb2gb(storage)),
        ]
