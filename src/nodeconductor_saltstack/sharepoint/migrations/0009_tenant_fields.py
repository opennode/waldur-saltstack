# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0008_extend_status_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='initialization_status',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='personal_site_collection',
        ),
        migrations.AddField(
            model_name='sharepointtenant',
            name='admin',
            field=models.ForeignKey(related_name='+', blank=True, to='sharepoint.User', null=True),
            preserve_default=True,
        ),
    ]
