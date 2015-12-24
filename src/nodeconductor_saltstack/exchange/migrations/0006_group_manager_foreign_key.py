# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0005_contact_group_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='manager_email',
        ),
        migrations.AddField(
            model_name='group',
            name='manager',
            field=models.ForeignKey(related_name='groups', default=1, to='exchange.User'),
            preserve_default=False,
        ),
    ]
