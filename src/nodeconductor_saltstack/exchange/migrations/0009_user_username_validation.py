# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0008_user_unique_together_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(regex=b"^[A-Z, a-z, 0-9, ., !, #, $, %, &, ', *, +, -, /, =, ?, ^, _, `]+$", message=b"Field value is not valid. Valid values are: Strings formed with characters from A to Z (uppercase or lowercase), digits from 0 to 9, !, #, $, %, &, ', *, +, -, /, =, ?, ^, _, `")]),
            preserve_default=True,
        ),
    ]
