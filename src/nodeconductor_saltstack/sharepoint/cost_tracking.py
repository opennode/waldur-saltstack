from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from .models import SharepointTenant


class Type(object):
    USAGE = 'usage'
    STORAGE = 'storage'

    STORAGE_KEY = '1 MB'
    USAGE_KEY = 'basic'

    CHOICES = {
        USAGE: USAGE_KEY,
        STORAGE: STORAGE_KEY,
    }


class SaltStackCostTrackingBackend(CostTrackingBackend):
    NUMERICAL = [Type.STORAGE]

    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(SharepointTenant)
        for item, key in Type.CHOICES.iteritems():
            yield DefaultPriceListItem(item_type=item, key=key, resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, resource):
        tenant = resource
        storage = tenant.quotas.get(name=SharepointTenant.Quotas.storage).usage
        return [
            (Type.USAGE, Type.CHOICES[Type.USAGE], 1),
            (Type.STORAGE, Type.CHOICES[Type.STORAGE], storage),
        ]
