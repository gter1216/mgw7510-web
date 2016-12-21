# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0005_auto_20161219_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='username',
            field=models.EmailField(max_length=80),
        ),
    ]
