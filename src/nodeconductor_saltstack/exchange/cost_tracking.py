from nodeconductor.cost_tracking import CostTrackingStrategy, CostTrackingRegister, ConsumableItem

from . import models


class ExchangeTenantStrategy(CostTrackingStrategy):
    resource_class = models.ExchangeTenant

    class Types(object):
        SUPPORT = 'support'
        STORAGE = 'storage'

    class Keys(object):
        STORAGE = '1 GB'
        SUPPORT = 'premium'

    @classmethod
    def get_consumable_items(cls):
        return [
            ConsumableItem(item_type=cls.Types.STORAGE, key=cls.Keys.STORAGE, name='1 GB of storage', units='GB'),
            ConsumableItem(item_type=cls.Types.SUPPORT, key=cls.Keys.SUPPORT, name='Support: premium'),
        ]

    @classmethod
    def get_configuration(cls, tenant):
        storage = tenant.quotas.get(name=models.ExchangeTenant.Quotas.mailbox_size).usage
        return {
            ConsumableItem(item_type=cls.Types.STORAGE, key=cls.Keys.STORAGE): float(storage) / 1024,
            ConsumableItem(item_type=cls.Types.SUPPORT, key=cls.Keys.SUPPORT): 1,
        }


CostTrackingRegister.register_strategy(ExchangeTenantStrategy)
