# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_saltstack', '0003_add_error_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saltstackserviceprojectlink',
            name='exchange_target',
        ),
        migrations.RemoveField(
            model_name='saltstackserviceprojectlink',
            name='sharepoint_target',
        ),
    ]
