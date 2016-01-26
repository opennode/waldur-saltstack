# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0006_site_collections'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sharepointtenant',
            old_name='users_site_collection',
            new_name='personal_site_collection',
        ),
        migrations.AlterField(
            model_name='sitecollection',
            name='access_url',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sitecollection',
            name='site_url',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sitecollection',
            name='template',
            field=models.ForeignKey(related_name='site_collections', blank=True, to='sharepoint.Template', null=True),
            preserve_default=True,
        ),
    ]
