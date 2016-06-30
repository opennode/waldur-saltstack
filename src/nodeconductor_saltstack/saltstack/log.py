from nodeconductor.logging.loggers import EventLogger, event_logger
from nodeconductor_saltstack.saltstack.models import SaltStackProperty


class SaltStackPropertyEventLogger(EventLogger):
    property = SaltStackProperty

    class Meta:
        event_types = (
            'saltstack_property_creation_succeeded',
            'saltstack_property_update_succeeded',
            'saltstack_property_deletion_succeeded',
        )


event_logger.register('saltstack_property', SaltStackPropertyEventLogger)
