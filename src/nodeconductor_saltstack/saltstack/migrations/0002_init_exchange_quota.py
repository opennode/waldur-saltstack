# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from uuid import uuid4

from django.contrib.contenttypes.models import ContentType
from django.db import migrations


EXCHANGE_STORAGE_QUOTA = 'exchange_storage'
DEFAULT_EXCHANGE_STORAGE_LIMIT = 50 * 1024


def init_quotas(apps, schema_editor):
    Quota = apps.get_model('quotas', 'Quota')
    SaltStackServiceProjectLink = apps.get_model('saltstack', 'SaltStackServiceProjectLink')
    spl_ct = ContentType.objects.get_for_model(SaltStackServiceProjectLink)

    for spl in SaltStackServiceProjectLink.objects.all():
        if not Quota.objects.filter(content_type_id=spl_ct.id, object_id=spl.id, name=EXCHANGE_STORAGE_QUOTA):
            Quota.objects.create(
                uuid=uuid4(), name=EXCHANGE_STORAGE_QUOTA, limit=DEFAULT_EXCHANGE_STORAGE_LIMIT, usage=0,
                content_type_id=spl_ct.id, object_id=spl.id)


class Migration(migrations.Migration):

    dependencies = [
        ('saltstack', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_quotas),
    ]
