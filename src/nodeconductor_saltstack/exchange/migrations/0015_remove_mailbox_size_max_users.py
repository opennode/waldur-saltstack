# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0014_group_delivery_members'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exchangetenant',
            name='mailbox_size',
        ),
        migrations.RemoveField(
            model_name='exchangetenant',
            name='max_users',
        ),
    ]
