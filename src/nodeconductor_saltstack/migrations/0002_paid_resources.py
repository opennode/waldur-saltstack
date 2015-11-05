# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.db import models, migrations
from nodeconductor.cost_tracking import CostConstants


def generate_pricelist(apps, schema_editor):
    DefaultPriceListItem = apps.get_model('cost_tracking', 'DefaultPriceListItem')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    domain_ct = ContentType.objects.get(app_label='nodeconductor_saltstack', model='domain')
    site_ct = ContentType.objects.get(app_label='nodeconductor_saltstack', model='site')

    DefaultPriceListItem.objects.create(
        uuid=uuid.uuid4().hex,  # autocreation doesn't work for whatever reason
        resource_content_type=domain_ct,
        item_type=CostConstants.PriceItem.STORAGE,
        name='Storage',
        key='1 GB',
        value=1,
    )

    DefaultPriceListItem.objects.create(
        uuid=uuid.uuid4().hex,
        resource_content_type=domain_ct,
        item_type=CostConstants.PriceItem.USERS,
        name='Mailboxes',
        key='',
        value=1,
    )

    DefaultPriceListItem.objects.create(
        uuid=uuid.uuid4().hex,
        resource_content_type=site_ct,
        item_type=CostConstants.PriceItem.STORAGE,
        name='Storage',
        key='1 GB',
        value=1,
    )

    DefaultPriceListItem.objects.create(
        uuid=uuid.uuid4().hex,
        resource_content_type=site_ct,
        item_type=CostConstants.PriceItem.USAGE,
        name='Usage',
        key='',
        value=1,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_saltstack', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('cost_tracking', '__latest__'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='billing_backend_id',
            field=models.CharField(help_text=b'ID of a resource in backend', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='domain',
            name='last_usage_update_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='site',
            name='billing_backend_id',
            field=models.CharField(help_text=b'ID of a resource in backend', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='site',
            name='last_usage_update_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=generate_pricelist,
            reverse_code=None,
            atomic=True,
        ),
    ]
