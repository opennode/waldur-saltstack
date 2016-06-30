# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0009_tenant_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecollection',
            name='type',
            field=models.CharField(default=b'regular', max_length=30, choices=[(b'main', b'main'), (b'admin', b'admin'), (b'personal', b'personal'), (b'regular', b'regular')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='personal_site_collection',
            field=models.ForeignKey(related_name='+', blank=True, to='sharepoint.SiteCollection', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
