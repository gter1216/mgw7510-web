# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mgw7510.models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0013_auto_20170103_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='userInputFile',
            field=models.FileField(null=True, upload_to=mgw7510.models.get_upload_path, blank=True),
        ),
        migrations.AddField(
            model_name='webuser',
            name='userInputFilePath',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
