# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saltstack', '0003_unique_spl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saltstackserviceprojectlink',
            name='error_message',
        ),
        migrations.RemoveField(
            model_name='saltstackserviceprojectlink',
            name='state',
        ),
    ]
