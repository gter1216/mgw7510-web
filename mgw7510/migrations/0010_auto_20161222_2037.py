# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0009_webuser_userworkdir'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='userWorkDir',
            field=models.CharField(max_length=100),
        ),
    ]
