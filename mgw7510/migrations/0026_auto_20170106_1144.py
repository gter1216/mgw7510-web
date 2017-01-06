# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0025_auto_20170106_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='ceDeployState',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
