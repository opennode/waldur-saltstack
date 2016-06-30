# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0012_more_members_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='delivery_members',
        ),
    ]
