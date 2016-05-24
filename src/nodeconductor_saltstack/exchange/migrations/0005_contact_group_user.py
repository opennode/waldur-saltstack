# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields

import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0004_init_quotas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(db_index=True, max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(related_name='+', to='exchange.ExchangeTenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(db_index=True, max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('manager_email', models.EmailField(max_length=255)),
                ('tenant', models.ForeignKey(related_name='+', to='exchange.ExchangeTenant')),
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
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(db_index=True, max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('mailbox_size', models.PositiveSmallIntegerField(help_text=b'Maximum size of mailbox, MB')),
                ('tenant', models.ForeignKey(related_name='+', to='exchange.ExchangeTenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
