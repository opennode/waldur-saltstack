from django.contrib.contenttypes.models import ContentType

from . import models
from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem
from nodeconductor.structure import ServiceBackend


class PriceItemTypes(object):
    USAGE = 'usage'
    USERS = 'users'
    STORAGE = 'storage'


class SaltStackCostTrackingBackend(CostTrackingBackend):
    STORAGE_KEY = '1 GB'
    USERS_KEY = 'mailboxes'
    USAGE_KEY = 'basic'

    @classmethod
    def get_default_price_list_items(cls):
        domain_content_type = ContentType.objects.get_for_model(models.Domain)
        site_content_type = ContentType.objects.get_for_model(models.Site)
        items = []
        # site usage
        items.append(DefaultPriceListItem(
            item_type=PriceItemTypes.USAGE, key=cls.USAGE_KEY, resource_content_type=site_content_type))
        # domain users
        items.append(DefaultPriceListItem(
            item_type=PriceItemTypes.USERS, key=cls.USERS_KEY, resource_content_type=domain_content_type))
        # site and domain storage
        items.append(DefaultPriceListItem(
            item_type=PriceItemTypes.STORAGE, key=cls.STORAGE_KEY, resource_content_type=site_content_type))
        items.append(DefaultPriceListItem(
            item_type=PriceItemTypes.STORAGE, key=cls.STORAGE_KEY, resource_content_type=domain_content_type))
        return items

    @classmethod
    def get_used_items(cls, resource):
        if isinstance(resource, models.Domain):
            return cls._get_domain_used_items(resource)
        elif isinstance(resource, models.Site):
            return cls._get_site_used_items(resource)

    @classmethod
    def _get_domain_used_items(cls, domain):
        return [
            (PriceItemTypes.USERS, cls.USERS_KEY, 0),  # XXX: get users count from backend
            (PriceItemTypes.STORAGE, cls.STORAGE_KEY, ServiceBackend.mb2gb(0)),  # XXX: get storage size from backend
        ]

    @classmethod
    def _get_site_used_items(cls, site):
        return [
            (PriceItemTypes.USAGE, cls.USAGE_KEY, 1),
            (PriceItemTypes.STORAGE, cls.STORAGE_KEY, ServiceBackend.mb2gb(0)),  # XXX: get storage size from backend
        ]
