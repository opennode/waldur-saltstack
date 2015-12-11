# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0002_site_tags'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Site',
            new_name='SharepointTenant',
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, db_index=True)),
                ('code', models.CharField(max_length=255)),
                ('settings', models.ForeignKey(related_name='+', to='structure.ServiceSettings')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('admin_id', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(related_name='users', to='sharepoint.SharepointTenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('url', models.URLField()),
                ('user', models.ForeignKey(related_name='sites', to='sharepoint.User')),
                ('tenant', models.ForeignKey(related_name='sites', to='sharepoint.SharepointTenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='template',
            unique_together=set([('settings', 'backend_id')]),
        ),
    ]
