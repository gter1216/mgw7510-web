# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0002_auto_20161219_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='email',
            field=models.EmailField(max_length=80),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='username',
            field=models.EmailField(max_length=80),
        ),
    ]
