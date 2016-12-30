# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='password',
            field=models.CharField(default=111111, max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='webuser',
            name='email',
            field=models.EmailField(max_length=100),
        ),
    ]
