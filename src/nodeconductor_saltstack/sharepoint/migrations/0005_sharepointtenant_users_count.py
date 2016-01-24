# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0004_sharepointtenant_storage_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharepointtenant',
            name='user_count',
            field=models.PositiveIntegerField(default=10, help_text=b'Maximum number of users in tenant'),
            preserve_default=False,
        ),
    ]
