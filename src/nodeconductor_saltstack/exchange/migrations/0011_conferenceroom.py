# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0010_group_members'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConferenceRoom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, db_index=True)),
                ('username', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255, blank=True)),
                ('phone', models.CharField(max_length=255, blank=True)),
                ('mailbox_size', models.PositiveSmallIntegerField(help_text=b'Maximum size of conference room mailbox, MB')),
                ('tenant', models.ForeignKey(related_name='+', to='exchange.ExchangeTenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
