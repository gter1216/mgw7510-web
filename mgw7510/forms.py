from django.forms import ModelForm
from mgw7510.models import WebUser
from django import forms

# inherit from class ModelForm
class WebUserForm(ModelForm):

    # username = forms.EmailField(error_messages="user name should not be empty")
    # password = forms.CharField(error_messages="password should not be empty")

    # password is an optional field
    password = forms.CharField(required=False)
    confirmPassword = forms.CharField(required=False)
    newPassword = forms.CharField(required=False)
    confirmNewPassword = forms.CharField(required=False)
    userWorkDir = forms.CharField(required=False)

    pakServerIp = forms.GenericIPAddressField(required=False)
    pakServerUsername = forms.CharField(required=False)
    pakServerPasswd = forms.CharField(required=False)
    pakServerFp = forms.CharField(required=False)

    seedVMIp = forms.GenericIPAddressField(required=False)
    seedVMUsername = forms.CharField(required=False)
    seedVMPasswd = forms.CharField(required=False)
    openrcAbsPath = forms.CharField(required=False)
    keypairAbsPath = forms.CharField(required=False)

    userInputFile = forms.FileField(label='Select a file',
                                    required=False)
    tmpPath = forms.CharField(required=False)
    userInputFileName = forms.CharField(required=False)
    progressBarData = forms.CharField(required=False)
    userInputUploadedFlag = forms.CharField(required=False)

    ceDeployState = forms.CharField(required=False)
    ceSelectRel = forms.CharField(required=False)
    ceSelectPak = forms.CharField(required=False)

    class Meta:
        model = WebUser  # inherit form WebUser
        fields = '__all__'
