# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saltstack', '0004_remove_spl_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='saltstackservice',
            options={'verbose_name': 'SaltStack service', 'verbose_name_plural': 'SaltStack service'},
        ),
    ]
