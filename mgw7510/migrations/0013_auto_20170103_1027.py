# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0012_auto_20161223_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='pakServerPasswd',
            field=models.CharField(default=b'initial', max_length=50),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='pakServerUsername',
            field=models.CharField(default=b'xxu', max_length=100),
        ),
    ]
