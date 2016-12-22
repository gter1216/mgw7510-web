from django.db import models

# Create your models here.

class WebUser(models.Model):
    username = models.EmailField(max_length=80)
    password = models.CharField(max_length=30)
    confirmPassword = models.CharField(max_length=30)
    newPassword = models.CharField(max_length=30)
    confirmNewPassword = models.CharField(max_length=30)
    userWorkDir = models.CharField(max_length=100)

    def __unicode__(self):
        return self.username