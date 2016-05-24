from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from .models import SharepointTenant


SUPPORT = 'support'
STORAGE = 'storage'
STORAGE_KEY = '1 MB'
SUPPORT_KEY = 'premium'


class SaltStackCostTrackingBackend(CostTrackingBackend):
    NUMERICAL = [STORAGE]

    @classmethod
    def get_default_price_list_items(cls):
        content_type = ContentType.objects.get_for_model(SharepointTenant)

        yield DefaultPriceListItem(
            item_type=STORAGE, key=STORAGE_KEY,
            resource_content_type=content_type)

        yield DefaultPriceListItem(
            item_type=SUPPORT, key=SUPPORT_KEY,
            resource_content_type=content_type)

    @classmethod
    def get_used_items(cls, tenant):
        storage = tenant.quotas.get(name=SharepointTenant.Quotas.storage).usage
        return [
            (STORAGE, STORAGE_KEY, storage),
            (SUPPORT, SUPPORT_KEY, 1),
        ]
