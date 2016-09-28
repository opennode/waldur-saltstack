# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0017_exchangetenant_publishing_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exchangetenant',
            name='billing_backend_id',
        ),
        migrations.RemoveField(
            model_name='exchangetenant',
            name='last_usage_update_time',
        ),
    ]
