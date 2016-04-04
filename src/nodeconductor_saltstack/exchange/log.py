from nodeconductor.logging.loggers import EventLogger, event_logger

from nodeconductor_saltstack.exchange.models import User, ExchangeTenant, Group


class ExchangeTenantEventLogger(EventLogger):
    tenant = ExchangeTenant

    class Meta:
        event_types = (
            'exchange_tenant_quota_update',
            'exchange_tenant_domain_change',
        )


class ExchangeUserEventLogger(EventLogger):
    affected_user = User

    class Meta:
        event_types = (
            'exchange_user_password_reset',
        )


class ExchangeGroupDeliveryMemberEventLogger(EventLogger):
    group = Group

    class Meta:
        event_types = (
            'exchange_group_delivery_member_add',
            'exchange_group_delivery_member_remove',
        )


class ExchangeGroupMemberEventLogger(EventLogger):
    group = Group

    class Meta:
        event_types = (
            'exchange_group_member_add',
            'exchange_group_member_remove',
        )


class ExchangeUserMemberEventLogger(EventLogger):
    affected_user = User

    class Meta:
        event_types = (
            'exchange_user_send_on_behalf_member_add',
            'exchange_user_send_on_behalf_member_remove',
            'exchange_user_send_as_member_add',
            'exchange_user_send_as_member_remove',
        )


event_logger.register('exchange_user', ExchangeUserEventLogger)
event_logger.register('exchange_tenant', ExchangeTenantEventLogger)
event_logger.register('exchange_group_delivery_member', ExchangeGroupDeliveryMemberEventLogger)
event_logger.register('exchange_group_member', ExchangeGroupMemberEventLogger)
event_logger.register('exchange_user_member', ExchangeUserMemberEventLogger)
