# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import gm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('exchange', '0013_remove_group_delivery_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='delivery_members',
            field=gm2m.fields.GM2MField(through_fields=(b'gm2m_src', b'gm2m_tgt', b'gm2m_ct', b'gm2m_pk')),
            preserve_default=True,
        ),
    ]
