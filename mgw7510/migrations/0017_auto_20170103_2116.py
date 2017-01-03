# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0016_webuser_usercedeploydir'),
    ]

    operations = [
        migrations.RenameField(
            model_name='webuser',
            old_name='userCeDeployDir',
            new_name='tmpPath',
        ),
    ]
