# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mgw7510.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.EmailField(max_length=100)),
                ('password', models.CharField(max_length=50)),
                ('confirmPassword', models.CharField(max_length=50)),
                ('newPassword', models.CharField(max_length=50)),
                ('confirmNewPassword', models.CharField(max_length=50)),
                ('userWorkDir', models.CharField(max_length=100)),
                ('pakServerIp', models.GenericIPAddressField(default=b'135.251.49.21')),
                ('pakServerUsername', models.CharField(default=b'xxu', max_length=100)),
                ('pakServerPasswd', models.CharField(default=b'initial', max_length=50)),
                ('pakServerFp', models.CharField(default=b'/viewstores/public/SLP', max_length=300)),
                ('seedVMIp', models.GenericIPAddressField(default=b'172.39.5.116')),
                ('seedVMUsername', models.CharField(default=b'root', max_length=100)),
                ('seedVMPasswd', models.CharField(default=b'newsys', max_length=50)),
                ('seedVMOpenrcAbsPath', models.CharField(default=b'/root/cloud-env/Rainbow-openrc.sh', max_length=300)),
                ('seedVMKeypairAbsPath', models.CharField(default=b'/root/cloud-env/BGW-keypair.pem', max_length=300)),
                ('userInputFile', models.FileField(null=True, upload_to=mgw7510.models.get_upload_path, blank=True)),
                ('tmpPath', models.CharField(max_length=100, null=True, blank=True)),
                ('userInputFileName', models.CharField(max_length=100, null=True, blank=True)),
                ('progressBarData', models.CharField(default=b'0', max_length=5)),
                ('userInputUploadedFlag', models.CharField(default=b'nok', max_length=5)),
                ('ceDeployState', models.CharField(default=b'initial', max_length=20)),
                ('ceSelectRel', models.CharField(max_length=10, null=True, blank=True)),
                ('ceSelectPak', models.CharField(max_length=10, null=True, blank=True)),
            ],
        ),
    ]
