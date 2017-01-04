# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0018_webuser_userinputfilename'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='progressBarData',
            field=models.CharField(default=b'0', max_length=5),
        ),
    ]
