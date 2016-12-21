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

    class Meta:
        model = WebUser  # inherit form WebUser
        fields = '__all__'
