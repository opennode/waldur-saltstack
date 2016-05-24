# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


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
