# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0010_auto_20161222_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='pakServerFp',
            field=models.CharField(default=b'/viewstores/public/SLP', max_length=500),
        ),
        migrations.AddField(
            model_name='webuser',
            name='pakServerIp',
            field=models.IPAddressField(default=b'135.251.49.21'),
        ),
        migrations.AddField(
            model_name='webuser',
            name='pakServerPasswd',
            field=models.CharField(default=b'', max_length=50),
        ),
        migrations.AddField(
            model_name='webuser',
            name='pakServerUsername',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='confirmNewPassword',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='confirmPassword',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='newPassword',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='password',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='username',
            field=models.EmailField(max_length=100),
        ),
    ]
