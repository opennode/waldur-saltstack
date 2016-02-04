# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('saltstack', '0002_init_exchange_quota'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='saltstackserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
    ]
