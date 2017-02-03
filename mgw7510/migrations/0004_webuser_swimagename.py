# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0003_auto_20170130_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='swImageName',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
