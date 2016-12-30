# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0008_auto_20161220_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='userWorkDir',
            field=models.FilePathField(default='/sd/'),
            preserve_default=False,
        ),
    ]
