# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0019_webuser_progressbardata'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='userInputUploadedFlag',
            field=models.CharField(default=b'nok', max_length=5),
        ),
    ]
