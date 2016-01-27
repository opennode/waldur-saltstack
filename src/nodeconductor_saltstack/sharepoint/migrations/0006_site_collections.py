# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields

import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0005_sharepointtenant_users_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, db_index=True)),
                ('site_url', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=500)),
                ('access_url', models.CharField(max_length=255, blank=True)),
                ('template', models.ForeignKey(related_name='site_collections', to='sharepoint.Template')),
                ('user', models.ForeignKey(related_name='site_collections', to='sharepoint.User')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='site',
            name='user',
        ),
        migrations.DeleteModel(
            name='Site',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='admin_login',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='admin_password',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='admin_url',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='site_name',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='site_url',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='storage_size',
        ),
        migrations.RemoveField(
            model_name='sharepointtenant',
            name='user_count',
        ),
        migrations.AddField(
            model_name='sharepointtenant',
            name='admin_site_collection',
            field=models.ForeignKey(related_name='+', blank=True, to='sharepoint.SiteCollection', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sharepointtenant',
            name='initialization_status',
            field=models.CharField(default=b'Not initialized', max_length=20, choices=[(b'Not initialized', b'Not initialized'), (b'Initializing', b'Initializing'), (b'Initialized', b'Initialized'), (b'Initialization failed', b'Initialization failed')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sharepointtenant',
            name='main_site_collection',
            field=models.ForeignKey(related_name='+', blank=True, to='sharepoint.SiteCollection', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sharepointtenant',
            name='users_site_collection',
            field=models.ForeignKey(related_name='+', blank=True, to='sharepoint.SiteCollection', null=True),
            preserve_default=True,
        ),
    ]
