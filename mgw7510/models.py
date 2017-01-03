from django.db import models

# Create your models here.

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

    def __unicode__(self):
        return self.username