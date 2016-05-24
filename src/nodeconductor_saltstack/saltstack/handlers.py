from __future__ import unicode_literals

import logging

from django.db import models

from .log import event_logger

logger = logging.getLogger(__name__)


def get_property_identifier(instance):
    property_identifier = '{property_name}'
    if 'email' in instance.get_log_fields():
        property_identifier += ' ({property_email})'
    elif 'username' in instance.get_log_fields():
        property_identifier += ' ({property_username})'
    return property_identifier


def is_field_loggable(instance, field):
    if field in ('admin_id', 'backend_id', 'password'):
        return False
    try:
        if isinstance(instance._meta.get_field(field), models.ForeignKey):
            return False
    except models.fields.FieldDoesNotExist:
        return False
    return True


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
            if not is_field_loggable(instance, field):
                continue
            changes.append('%s "%s" has been changed to "%s"' % (
                field, instance.tracker.previous(field), getattr(instance, field)))

        if not changes:
            return

        event_logger.saltstack_property.info(
            '%s %s has been updated in {resource_full_name}. Changes: %s.' % (
                instance.get_type_display_name(), get_property_identifier(instance), ', '.join(changes)),
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
