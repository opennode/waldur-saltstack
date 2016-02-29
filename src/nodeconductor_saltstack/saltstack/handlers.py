from __future__ import unicode_literals

import logging

from .log import event_logger

logger = logging.getLogger(__name__)


def log_saltstack_property_created(sender, instance, created=False, **kwargs):
    if created:
        event_logger.saltstack_property.info(
            '%s {property_name} has been created in {tenant_full_name}.' % instance.get_type_display_name(),
            event_type='saltstack_property_creation_succeeded',
            event_context={
                'property': instance,
            })
    else:
        event_logger.saltstack_property.info(
            '%s {property_name} has been updated in {tenant_full_name}.' % instance.get_type_display_name(),
            event_type='saltstack_property_update_succeeded',
            event_context={
                'property': instance,
            })


def log_saltstack_property_deleted(sender, instance, **kwargs):
    event_logger.saltstack_property.info(
        '%s {property_name} has been deleted from {tenant_full_name}.' % instance.get_type_display_name(),
        event_type='saltstack_property_deletion_succeeded',
        event_context={
            'property': instance,
        })
