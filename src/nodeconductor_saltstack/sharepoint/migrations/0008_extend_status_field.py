# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0007_site_collection_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharepointtenant',
            name='initialization_status',
            field=models.CharField(default=b'Not initialized', max_length=30, choices=[(b'Not initialized', b'Not initialized'), (b'Initializing', b'Initializing'), (b'Initialized', b'Initialized'), (b'Initialization failed', b'Initialization failed')]),
            preserve_default=True,
        ),
    ]
