from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem
from nodeconductor.structure import ServiceBackend

from .models import Tenant


class PriceItemTypes(object):
    USERS = 'users'
    STORAGE = 'storage'

    STORAGE_KEY = '1 GB'
    USERS_KEY = 'mailboxes'

    CHOICES = {
        USERS: USERS_KEY,
        STORAGE: STORAGE_KEY,
    }


class SaltStackCostTrackingBackend(CostTrackingBackend):
    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(Tenant)
        for item, key in PriceItemTypes.CHOICES.iteritems():
            yield DefaultPriceListItem(item_type=item, key=key, resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, resource):
        # XXX: get values from backend
        return [
            (PriceItemTypes.USERS, PriceItemTypes.CHOICES[PriceItemTypes.USERS], 0),
            (PriceItemTypes.STORAGE, PriceItemTypes.CHOICES[PriceItemTypes.STORAGE], ServiceBackend.mb2gb(0)),
        ]
