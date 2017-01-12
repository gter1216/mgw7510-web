from __future__ import division
from mgw7510.models import WebUser
from pexpect import pxssh
import pexpect
import logging
import shutil
import time
import re
import os


def get_pak_list(pak_ip,
                 pak_username,
                 pak_passwd,
                 pak_path):

    try:
        s = pxssh.pxssh()
        s.login(pak_ip, pak_username, pak_passwd, original_prompt='[$#>]')
        cmd1 = 'cd ' + pak_path
        s.sendline(cmd1)
        s.prompt()
        s.sendline('find ./ -name *qcow2')
        s.prompt()
        result = s.before
        s.logout()

        final_result = {'ok': re.findall(r'nokia.*?qcow2', result)}
        return final_result
    except pxssh.ExceptionPxssh, e:
        return {'nok': 'Failed login to pak server, please check settings!'}


def update_progress_bar(user, data):
    user.progressBarData = data
    user.save()


def clean_work(user):
    pass


def deployment_success(user, perform_clean_work):
    if perform_clean_work == "yes":
        # do clean work
        clean_work(user)

    update_progress_bar(user, "100")

    # shutdown logger
    logging.shutdown()


def deployment_failed(user, perform_clean_work):
    if perform_clean_work == "yes":
        # do clean work
        clean_work(user)

    update_progress_bar(user, "101")

    # shutdown logger
    logging.shutdown()


# general function to ssh to the specific host
def create_ssh_session(host, username, password, prompt):
    cmd = 'ssh ' + username + '@' + host

    logging.info('\n%s \n' % cmd)

    child = pexpect.spawn(cmd)
    ret = child.expect([pexpect.TIMEOUT, 'password:', 'Are you sure you want to continue connecting'], timeout=20)

    logging.info('\nret is %s \n' % ret)

    if ret == 0:
        raise Exception("\nssh to %s timeout \n" % host)
    elif ret == 1:
        child.sendline(password)
        child.expect(prompt)
    elif ret == 2:
        child.sendline("yes")
        ret = child.expect([pexpect.TIMEOUT, 'password'], timeout=20)
        if ret == 0:
            raise Exception("\nssh to %s timeout \n" % host)
        elif ret == 1:
            child.sendline(password)
            child.expect(prompt)

    # successful login to the host
    logging.info('\n%s \n' % child.before)
    return child


def update_progbar_by_scp(user, session, prompt, scp_step, progbar_total_incr):

    scp_list = range(1, 100, scp_step)
    scp_len = len(scp_list)

    progbar_step = round(progbar_total_incr/(scp_len+1))
    progbar_step = int(progbar_step)

    scp_to = round(3600/(scp_len+1))
    scp_to = int(scp_to)

    print scp_list
    print scp_len
    print progbar_step
    print scp_to

    # [1, 4, ... , 97]
    for i_scp in scp_list:
        scp_exp = str(i_scp)+"%"
        session.expect(scp_exp, timeout=scp_to)
        logging.info('\n%s \n' % session.before)
        user.progressBarData = str(int(user.progressBarData) + progbar_step)
        user.save()

    session.expect(prompt, timeout=scp_to)
    logging.info('\n%s \n' % session.before)
    user.progressBarData = str(int(user.progressBarData) + progbar_step)
    user.save()