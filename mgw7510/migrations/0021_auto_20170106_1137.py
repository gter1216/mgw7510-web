# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgw7510', '0020_webuser_userinputuploadedflag'),
    ]

    operations = [
        migrations.AddField(
            model_name='webuser',
            name='ceDeployState',
            field=models.CharField(default=None, max_length=10),
        ),
        migrations.AddField(
            model_name='webuser',
            name='ceSelectPak',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='webuser',
            name='ceSelectRel',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
