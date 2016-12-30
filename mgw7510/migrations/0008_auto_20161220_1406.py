# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0007_remove_webuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='confirmNewPassword',
            field=models.CharField(default=datetime.datetime(2016, 12, 20, 14, 6, 9, 987290, tzinfo=utc), max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='webuser',
            name='newPassword',
            field=models.CharField(default=222, max_length=30),
            preserve_default=False,
        ),
    ]
