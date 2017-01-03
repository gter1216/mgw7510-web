# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0011_auto_20161223_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='pakServerIp',
            field=models.GenericIPAddressField(default=b'135.251.49.21'),
        ),
    ]
