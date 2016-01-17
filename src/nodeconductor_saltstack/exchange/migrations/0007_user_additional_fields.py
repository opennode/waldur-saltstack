# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeconductor_saltstack.exchange.validators


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0006_group_manager_foreign_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='manager',
            field=models.ForeignKey(blank=True, to='exchange.User', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='office',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='title',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='exchangetenant',
            name='domain',
            field=models.CharField(max_length=255, validators=[nodeconductor_saltstack.exchange.validators.domain_validator]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        ),
    ]
