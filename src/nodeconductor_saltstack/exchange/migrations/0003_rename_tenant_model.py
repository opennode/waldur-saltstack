# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_fsm
import nodeconductor.core.models
import django.db.models.deletion
import nodeconductor.logging.log
import uuidfield.fields
import taggit.managers
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('saltstack', '0001_initial'),
        ('exchange', '0002_tenant_tags'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tenant',
            new_name='ExchangeTenant',
        ),
    ]
