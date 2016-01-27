# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0009_user_username_validation'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to='exchange.User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
