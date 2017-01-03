# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0015_remove_webuser_userinputfilepath'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='userCeDeployDir',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
