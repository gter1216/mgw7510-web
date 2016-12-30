"""R01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

#admin.autodiscover()

urlpatterns = [
    # http://135.251.216.181/, This is an homepage
    url(r'^$','mgw7510.views.index' ),

    # http://135.251.216.181/under-consturction/
    url(r'^under-construction/$','mgw7510.views.under_con'),

    # http://135.251.216.181/signin/, When click signin on the homepage,
    # this is an target url for the post, so there is no $ in the end
    url(r'^signin/', 'mgw7510.views.signin'),

    # http://135.251.216.181/register/, This is an register page
    url(r'^register/$','mgw7510.views.register'),

    # http://135.251.216.181/register/signup, When click signup on the register page,
    # this is an target url for the form post, so there is no $ in the end
    url(r'^register/signup/','mgw7510.views.signup'),

    # http://135.251.216.181/change-password/submit, When click submit on the change password page
    url(r'^change-password/ok/', 'mgw7510.views.changePasswdOk'),

    # http://135.251.216.181/change-password/, This is an page used to change the password
    url(r'^change-password/$', 'mgw7510.views.changePasswd'),

    # http://135.251.216.181/forget-password/,
    url(r'^forget-password/', 'mgw7510.views.forgetPasswd'),

    # http://135.251.216.181/login, This is the home page after log in
    url(r'^login-in/(.+)/$', 'mgw7510.views.loginIn'),

    url(r'^settings/$', 'mgw7510.views.settings'),

    # http://135.251.216.181/logout, This is the page after the user logged out
    url(r'^logout/$', 'mgw7510.views.logout'),

    # http://135.251.216.181/admin, This is an admin page to manage all registered users
    url(r'^admin/', include(admin.site.urls)),

    # http://135.251.216.181/ce-deploy, This is an home page for ce auto deployment
    url(r'^ce-deploy/$', 'mgw7510.views.ceDeploy'),

    # http://135.251.216.181/ce-deploy, This is an home page for ce auto deployment
    url(r'^ce-deploy/check-pak/$', 'mgw7510.views.ceCheckPak'),

]




