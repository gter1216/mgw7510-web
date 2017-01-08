from django.db import models
import os

# Create your models here.

def get_upload_path(instance, filename):
    temp_path = os.path.join(instance.tmpPath, filename)
    print temp_path
    return temp_path

class WebUser(models.Model):
    username = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)
    confirmPassword = models.CharField(max_length=50)
    newPassword = models.CharField(max_length=50)
    confirmNewPassword = models.CharField(max_length=50)
    userWorkDir = models.CharField(max_length=100)

    # CE Deployment, add default value
    pakServerIp = models.GenericIPAddressField(max_length=50, default="135.251.49.21")
    pakServerUsername = models.CharField(max_length=100, default="xxu")
    pakServerPasswd = models.CharField(max_length=50, default="initial")
    pakServerFp = models.CharField(max_length=300, default="/viewstores/public/SLP")

    seedVMIp = models.GenericIPAddressField(max_length=50, default="172.39.5.116")
    seedVMUsername = models.CharField(max_length=100, default="root")
    seedVMPasswd = models.CharField(max_length=50, default="newsys")
    seedVMOpenrcAbsPath = models.CharField(max_length=300, default="/root/cloud-env/Rainbow-openrc.sh")
    seedVMKeypairAbsPath = models.CharField(max_length=300, default="/root/cloud-env/BGW-keypair.pem")

    userInputFile = models.FileField(null=True,
                                     blank=True,
                                     upload_to=get_upload_path)

    tmpPath = models.CharField(null=True,
                               blank=True,
                               max_length=100)

    userInputFileName = models.CharField(null=True,
                                         blank=True,
                                         max_length=100)

    progressBarData = models.CharField(default="0",
                                       max_length=5)

    # default is nok, which means that user input file not uploaded
    userInputUploadedFlag = models.CharField(default="nok",
                                             max_length=5)

    ceDeployState = models.CharField(default="initial",
                                     max_length=20)

    ceSelectRel = models.CharField(null=True,
                                   blank=True,
                                   max_length=10)

    ceSelectPak = models.CharField(null=True,
                                   blank=True,
                                   max_length=10)

    def __unicode__(self):
        return self.username