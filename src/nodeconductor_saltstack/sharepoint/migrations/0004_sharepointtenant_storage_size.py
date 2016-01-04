# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0003_new_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharepointtenant',
            name='storage_size',
            field=models.PositiveIntegerField(default=1, help_text=b'Maximum size of tenants, MB'),
            preserve_default=False,
        ),
    ]
