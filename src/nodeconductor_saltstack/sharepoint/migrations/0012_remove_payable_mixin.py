# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0011_sharepointtenant_publishing_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='billing_backend_id',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='last_usage_update_time',
        ),
    ]
