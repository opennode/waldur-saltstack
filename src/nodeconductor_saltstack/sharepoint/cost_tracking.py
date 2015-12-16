from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem
from nodeconductor.structure import ServiceBackend

from .models import SharepointTenant


class PriceItemTypes(object):
    USAGE = 'users'
    STORAGE = 'storage'

    STORAGE_KEY = '1 GB'
    USAGE_KEY = 'basic'

    CHOICES = {
        USAGE: USAGE_KEY,
        STORAGE: STORAGE_KEY,
    }


class SaltStackCostTrackingBackend(CostTrackingBackend):
    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(SharepointTenant)
        for item, key in PriceItemTypes.CHOICES.iteritems():
            yield DefaultPriceListItem(item_type=item, key=key, resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, resource):
        backend = resource.get_backend()
        storage = sum(s.usage for s in backend.sites.list())
        return [
            (PriceItemTypes.USAGE, PriceItemTypes.CHOICES[PriceItemTypes.USAGE], 1),
            (PriceItemTypes.STORAGE, PriceItemTypes.CHOICES[PriceItemTypes.STORAGE], ServiceBackend.mb2gb(storage)),
        ]
