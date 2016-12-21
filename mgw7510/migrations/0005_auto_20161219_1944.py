# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0004_webuser_confirmpassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webuser',
            name='username',
            field=models.CharField(max_length=80),
        ),
    ]
