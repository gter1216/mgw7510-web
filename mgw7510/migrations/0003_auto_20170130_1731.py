# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0002_auto_20170109_0424'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='ceDeployProcess',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='yactServerDIFAbsPath',
            field=models.CharField(default=b'/home/darcy/oam_linux_DIF_FILL/7510-CE/C710.ad1115/', max_length=300),
        ),
    ]
