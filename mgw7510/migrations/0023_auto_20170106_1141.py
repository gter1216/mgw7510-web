# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0022_auto_20170106_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='ceDeployState',
            field=models.CharField(default=b'initial', max_length=20),
        ),
    ]
