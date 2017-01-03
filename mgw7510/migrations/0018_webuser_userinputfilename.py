# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0017_auto_20170103_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='userInputFileName',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
