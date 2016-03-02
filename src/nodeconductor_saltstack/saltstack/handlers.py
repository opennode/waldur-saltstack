from __future__ import unicode_literals

import logging

from .log import event_logger

logger = logging.getLogger(__name__)


def get_property_identifier(instance):
    property_identifier = '{property_name}'
    if 'email' in instance.get_log_fields():
        property_identifier += ' ({property_email})'
    elif 'username' in instance.get_log_fields():
        property_identifier += ' ({property_username})'
    return property_identifier


def log_saltstack_property_created(sender, instance, created=False, **kwargs):
    if created:
        event_logger.saltstack_property.info(
            '%s %s has been created in {resource_full_name}.' % (
                instance.get_type_display_name(), get_property_identifier(instance)),
            event_type='saltstack_property_creation_succeeded',
            event_context={
                'property': instance,
            })
    else:
        changes = []
        for field in instance.tracker.changed():
            if field == 'password':
                continue
            changes.append('%s "%s" has been changed to "%s"' % (
                field, instance.tracker.previous(field), getattr(instance, field)))

        message = '%s %s has been updated in {resource_full_name}.' % (
                instance.get_type_display_name(), get_property_identifier(instance))
        if changes:
            message += ' Changes: %s.' % ', '.join(changes)

        event_logger.saltstack_property.info(
            message,
            event_type='saltstack_property_update_succeeded',
            event_context={
                'property': instance,
            })


def log_saltstack_property_deleted(sender, instance, **kwargs):
    event_logger.saltstack_property.info(
        '%s %s has been deleted from {resource_full_name}.' % (
            instance.get_type_display_name(), get_property_identifier(instance)),
        event_type='saltstack_property_deletion_succeeded',
        event_context={
            'property': instance,
        })
