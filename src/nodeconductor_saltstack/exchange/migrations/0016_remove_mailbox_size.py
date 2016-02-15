# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0015_remove_mailbox_size_max_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conferenceroom',
            name='mailbox_size',
        ),
        migrations.RemoveField(
            model_name='user',
            name='mailbox_size',
        ),
    ]
