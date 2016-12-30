from django.shortcuts import render
from django.http import HttpResponse
from mgw7510.forms import WebUserForm
from mgw7510.models import WebUser
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
import os
import logging


logger = logging.getLogger("django")

# Create your views here.

# request an home page
def index(request):

    # if find the cookie, then we think the user has been logged in
    uname = request.session.get('username')
    if uname:
        return render(request, 'login_in.html', {'user': uname})

    # first par:  request
    # second par: auto search template path
    logger.debug("This is an debug message by xuxiao: web user request home page")
    return render(request,'index.html')

# under construction page
def under_con(request):
    return render(request,'under-construction.html')


# register page
def register(request):
    return render(request,'register/register.html')

# change password page
def changePasswd(request):
    p1 = request.GET.get('p1')
    return render(request, 'register/change_password.html', {'paramUser': p1})

# click submit on the changepassword page
def changePasswdOk(request):
    if request.method == 'POST':
        wuf = WebUserForm(request.POST)
        if wuf.is_valid():
            cleanData = wuf.cleaned_data

            cp_uname = cleanData['username']
            cp_old_passwd = cleanData['password']
            cp_new_passwd = cleanData['newPassword']
            cp_confirm_new_passwd = cleanData['confirmNewPassword']

            # check if the user exist
            UserExist = WebUser.objects.filter(username__exact=cp_uname)

            if not UserExist:
                return HttpResponse('user not exist, please check!')
            else:
                # if user exist, get the user object, and then get
                # the attr password of the object
                MatchUser = WebUser.objects.get(username=cp_uname)
                db_passwd = MatchUser.password

                if db_passwd == cp_old_passwd:
                    # auth passed
                    if cp_new_passwd == cp_confirm_new_passwd:
                        # change db_passwd to cp_new_passwd
                        MatchUser.password = cp_new_passwd
                        MatchUser.save()
                        # clear the cookie
                        try:
                            del request.session['username']
                        except KeyError:
                            pass
                        return HttpResponse('ok')
                    else:
                        return HttpResponse('new password and confirm new password not same')
                else:
                    return HttpResponse('old password is not correct')
        else:
            return HttpResponse('invalid input')
    else:
        return HttpResponse('not post method')


# regist a new web user
def signup(request):
    if request.method == 'POST':
        logger.debug("The sign up form is posted to django")

        hp_uname = request.POST['username']
        hp_passwd = request.POST['password']
        hp_cpasswd = request.POST['confirmPassword']

        if (hp_passwd != hp_cpasswd):
            return HttpResponse('password not same, please check')

        # database query,
        userExist = WebUser.objects.filter(username__exact=hp_uname)

        if userExist:
            return HttpResponse('user exists, please change to another username')
        else:
            # set cookie; write username into cookie, valid timer is 3600s
            request.session['username'] = hp_uname
            # request.set_cookie('username', username, 3600)

            # create directory per user
            user_work_dir = hp_uname.replace("@","_")
            user_work_dir = settings.BASE_DIR + "/UserWorkDir/" + user_work_dir
            os.mkdir(user_work_dir)

            WebUser.objects.create(username=hp_uname,
                                   password=hp_passwd,
                                   userWorkDir=user_work_dir)
            return HttpResponse('ok')

def loginIn(request, loginParam):
    print loginParam

    # user is a template var
    return render(request, 'login_in.html', {'user':loginParam})

def logout(request):

    # delete the cookies
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect("/")

def signin(request):
    if request.method == 'POST':
        wuf = WebUserForm(request.POST)
        if wuf.is_valid():
            cleanData = wuf.cleaned_data
            hp_uname = cleanData['username']
            hp_passwd = cleanData['password']

            # check if the user exist
            UserExist = WebUser.objects.filter(username__exact=hp_uname)

            if not UserExist:
                return HttpResponse('user not exist, please register first!')
            else:
                # if user exist, get the user object, and then get
                # the attr password of the object
                MatchUser = WebUser.objects.get(username=hp_uname)
                passwd_db = MatchUser.password
                # print ("pasword in database is %s"%(passwd_db))
                if hp_passwd == passwd_db:
                    # auth passed
                    # then set cookie
                    request.session['username'] = hp_uname
                    return HttpResponse('ok')
                else:
                    return HttpResponse('password is not correct')
        else:
            return HttpResponse('username/password should not be empty \nusername should be email address ')
    else:
        return HttpResponse('not post method')

def forgetPasswd(request):
    if request.method == 'POST':
        wuf = WebUserForm(request.POST)
        if wuf.is_valid():
            cleanData = wuf.cleaned_data
            hp_uname = cleanData['username']

            # check if the user exist
            UserExist = WebUser.objects.filter(username__exact=hp_uname)

            if not UserExist:
                return HttpResponse('user not exist, please check!')
            else:
                MatchUser = WebUser.objects.get(username=hp_uname)
                passwd_db = MatchUser.password
                # send mail to the hp_uname and return ok
                passwd_info = 'Dear, \n\nyour password is '+passwd_db

                print passwd_info
                print [hp_uname]
                send_mail('Your own password in www.sbc.nokia.com(135.251.216.181)', # subject
                          passwd_info, # body
                          'no-reply@sbc.nokia.com', # from mail
                          [hp_uname] # to mail
                          )
                info = 'your password has been sent to ' + hp_uname
                return HttpResponse(info)
        else:
            return HttpResponse('username should not be empty \nusername should be email address ')
    else:
        return HttpResponse('not post method')

# request an home page for ce deploy
def ceDeploy(request):

    # if user logged
    uname = request.session.get('username')
    if uname:
        return render(request, 'ce_deployment/ce_deploy.html', {'user': uname})
    else:
        return HttpResponse("please login in first!")

# ce deploy process function
def ceCheckPak(request):
    if request.method == 'POST':
        # request.POST ====> <QueryDict: {u'selectPak': [u'none']}>
        # request.body ====> selectPak=none

        if request.POST.has_key('selectPak'):
            if request.POST['selectPak'] == 'none':
                print "ok"
                # query the ngnsvr11 to get package list and return it with JSON format


def settings(request):
    # if user logged
    uname = request.session.get('username')
    if uname:
        return render(request, 'settings.html', {'paramUser': uname})
    else:
        return HttpResponse("please login in first!")






