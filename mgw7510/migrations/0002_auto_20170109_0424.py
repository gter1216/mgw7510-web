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
            name='yactServerDIFAbsPath',
            field=models.CharField(default=b'/home/darcy/oam_linux_DIF_FILL/7510-CE/C710.ad1115', max_length=300),
        ),
        migrations.AddField(
            model_name='webuser',
            name='yactServerIp',
            field=models.GenericIPAddressField(default=b'135.251.49.19'),
        ),
        migrations.AddField(
            model_name='webuser',
            name='yactServerPasswd',
            field=models.CharField(default=b'initial', max_length=50),
        ),
        migrations.AddField(
            model_name='webuser',
            name='yactServerUsername',
            field=models.CharField(default=b'darcy', max_length=100),
        ),
        migrations.AddField(
            model_name='webuser',
            name='yactServerYactAbsPath',
            field=models.CharField(default=b'/home/darcy/YACT/', max_length=300),
        ),
    ]
