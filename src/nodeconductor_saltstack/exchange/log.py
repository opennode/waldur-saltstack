from nodeconductor.logging.log import EventLogger, event_logger

from nodeconductor_saltstack.exchange.models import User, ExchangeTenant


class ExchangeTenantEventLogger(EventLogger):
    tenant = ExchangeTenant

    class Meta:
        event_types = (
            'exchange_tenant_quota_update',
        )


class ExchangeUserEventLogger(EventLogger):
    affected_user = User

    class Meta:
        event_types = (
            'exchange_user_password_reset',
        )


event_logger.register('exchange_user', ExchangeUserEventLogger)
event_logger.register('exchange_tenant', ExchangeTenantEventLogger)
