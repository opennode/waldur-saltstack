# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_saltstack', '0004_remove_useless_spl_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='error_message',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='site',
            name='error_message',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
