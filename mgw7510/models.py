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
    pakServerIp = models.GenericIPAddressField(max_length=50,
                                               default="135.251.49.21")

    pakServerUsername = models.CharField(max_length=100,
                                         default="xxu")

    pakServerPasswd = models.CharField(max_length=50,
                                       default="initial")

    pakServerFp = models.CharField(max_length=500,
                                   default="/viewstores/public/SLP")

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

    def __unicode__(self):
        return self.username