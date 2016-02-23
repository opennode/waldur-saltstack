from __future__ import unicode_literals

import logging
from nodeconductor.structure import SupportedServices

from ..saltstack.log import event_logger


logger = logging.getLogger(__name__)


def log_saltstack_property_created(sender, instance, created=False, **kwargs):
    property_type = SupportedServices._get_model_str(instance)
    property_type_display = property_type.replace('.', ' ').capitalize()
    if created:
        event_logger.saltstack_property.info(
            '%s {property_name} has been created.' % property_type_display,
            event_type='saltstack_property_creation_succeeded',
            event_context={
                'property': instance,
                'property_type': property_type,
            })
    else:
        event_logger.saltstack_property.info(
            '%s {property_name} has been updated.' % property_type,
            event_type='saltstack_property_update_succeeded',
            event_context={
                'property': instance,
            })


def log_saltstack_property_deleted(sender, instance, **kwargs):
    property_type = SupportedServices._get_model_str(instance)
    property_type_display = property_type.replace('.', ' ').capitalize()

    event_logger.saltstack_property.info(
        '%s {property_name} has been deleted.' % property_type,
        event_type='saltstack_property_deletion_succeeded',
        event_context={
            'property': instance,
            'property_type': property_type,
        })


