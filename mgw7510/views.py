from django.shortcuts import render
from django.http import HttpResponse
from mgw7510.forms import WebUserForm
from mgw7510.models import WebUser
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
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

        # it will print at uwsgi log
        print "The sign up form is posted to django"

        wuf = WebUserForm(request.POST)

        if wuf.is_valid():
            print "form is valid"

            # get data form post
            cleanData = wuf.cleaned_data
            hp_uname = cleanData['username']
            hp_passwd = cleanData['password']
            hp_cpasswd = cleanData['confirmPassword']

            if (hp_passwd != hp_cpasswd):
                return HttpResponse('password not same, please check')

            # database query,
            userExist = WebUser.objects.filter(username__exact=hp_uname)

            if userExist:
                return HttpResponse('user exists, please change to another username')
            else:
                # commit data form browser to the database
                wuf.save()
                # >> > b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
                # >> > b.save()

                # set cookie; write username into cookie, valid timer is 3600s
                request.session['username'] = hp_uname
                # request.set_cookie('username', username, 3600)
                return HttpResponse('ok')

            # wuf_info = wuf.save()
            # wuf_info.save()

            # save data to the database


            # user = auth.authenticate(email=emal,password=password)
            #
            # if user is not None and user.is_active
            #     auth.login(request,user)
            #     return

            # commit data form browser to the database
            # webUserForm.save()

        else:
            print "form is invalid"
            return HttpResponse('input is not valid')

        # # parse json data
        # rec_data = json.loads(request.body)
        #
        # print rec_data
        #
        # username = rec_data['username']
        # email = rec_data['email']
        # password = rec_data['password']
        # confirmPassword = rec_data['confirmPassword']
        #
        # #logger.debug(json_data)
        # #logger.debug('user name: %s'%username)
        # logger.debug("user name: %s, email: %s, password: %s"%(username,emial,password))
        #
        # if form.is_valid():
        #     return HttpResponse('ok')
        # else:
        #     return HttpResponse('failed')


# sign up register form,  get form data by "POST"

# from django import forms
# from django.http import HttpResponse
#
# class UserForm(forms.Form):
#     name = form.CharField()
#
# def signup(req):
#     if req.method == 'POST':
#         form = UserForm(req.POST)
#         if form.is_valid():
#             print form.cleaned_data
#             return HttpResponse('ok')
#     else:
#         form = UserForm()
#     return render_to_response('register.html',{'form':form})


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




