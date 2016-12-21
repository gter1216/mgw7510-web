# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0003_auto_20161219_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='confirmPassword',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
    ]
