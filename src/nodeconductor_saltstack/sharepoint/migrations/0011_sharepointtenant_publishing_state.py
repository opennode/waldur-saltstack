# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0010__site_collection_types_user_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharepointtenant',
            name='publishing_state',
            field=models.CharField(default='not published', max_length=30, choices=[('not published', 'Not published'), ('published', 'Published'), ('requested', 'Requested')]),
            preserve_default=True,
        ),
    ]
