# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0011_conferenceroom'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='delivery_members',
            field=models.ManyToManyField(related_name='+', to='exchange.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='senders_out',
            field=models.BooleanField(default=False, help_text=b'Delivery management for senders outside organizational unit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='send_as_members',
            field=models.ManyToManyField(related_name='send_as_members_rel_+', to='exchange.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='send_on_behalf_members',
            field=models.ManyToManyField(related_name='send_on_behalf_members_rel_+', to='exchange.User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='+', to='exchange.User'),
            preserve_default=True,
        ),
    ]
