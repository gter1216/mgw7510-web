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

    logging.info('\nDeployment failed, please check ERROR information \n')

    # shutdown logger
    logging.shutdown()


# general function to ssh to the specific host
def create_ssh_session(host, username, password, prompt):
    cmd = 'ssh ' + username + '@' + host

    logging.info('\n%s \n' % cmd)

    child = pexpect.spawn(cmd)
    ret = child.expect([pexpect.TIMEOUT, 'password:', 'Are you sure you want to continue connecting'], timeout=20)
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
    logging.info('%s \n' % child.before)
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


def get_qcow2_md5_from_pak(pak_server_info, qcow2_name, select_rel):
    try:
        pak_server_ip = pak_server_info["ip"]
        pak_server_username = pak_server_info["username"]
        pak_server_password = pak_server_info["passwd"]
        pak_server_fp = pak_server_info["fp"]
        pak_prompt = pak_server_info["prompt"]

        pak_session = create_ssh_session(pak_server_ip, pak_server_username, pak_server_password, pak_prompt)

        pak_cmd = "cd " + "`" + "find " + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
                  "-name " + qcow2_name + " -exec " + "dirname {} " + '\\;' + "`"

        pak_session.sendline(pak_cmd)
        pak_session.expect(pak_prompt)
        logging.info('\n%s \n' % pak_session.before)

        # do not need caculate MD5, comment the code
        # pak_session.sendline("md5sum " + qcow2_name)
        # pak_session.expect(pak_prompt)
        # result = pak_session.before
        # logging.info('\n%s \n' % result)
        # result = result.split()
        # pak_session.close()
        # return result[2]

        pak_session.sendline("more " + qcow2_name + ".md5")
        pak_session.expect(pak_prompt)
        result = pak_session.before
        logging.info('\n%s \n' % result)
        result = result.split()
        pak_session.close()
        return result[2]

    except Exception, e:
        logging.error('problem during ssh to pak server: %s \n' % str(e))
        return


def get_seedvm_qcow2_cached_flag(seedvm_info, qcow2_name, qcow2_md5):
    try:
        seedvm_ip = seedvm_info["ip"]
        seedvm_username = seedvm_info["username"]
        seedvm_passwd = seedvm_info["passwd"]
        seedvm_prompt = seedvm_info["prompt"]
        seedvm_cache_dir = seedvm_info["cache_dir"]

        seedvm_session = create_ssh_session(seedvm_ip, seedvm_username, seedvm_passwd, seedvm_prompt)

        # create seed vm cache dir
        # if exists, then rm it and then create it
        seedvm_cmd = "mkdir " + seedvm_cache_dir
        seedvm_session.sendline(seedvm_cmd)
        seedvm_ret = seedvm_session.expect([seedvm_prompt, 'File exists'])

        if seedvm_ret == 0:
            logging.info('\n%s \n' % seedvm_session.before)
        elif seedvm_ret == 1:
            # first match File exists, then match '~#' !!!!!!!!!!IMPORTANT!!!!!!!!!!
            seedvm_session.expect(seedvm_prompt)
            logging.info('\n%s \n' % seedvm_session.before)
            seedvm_session.sendline("rm -rf " + seedvm_work_dir)
            seedvm_session.expect(seedvm_prompt)
            logging.info('\n%s \n' % seedvm_session.before)
            seedvm_session.sendline(seedvm_cmd)
            seedvm_session.expect(seedvm_prompt)
            logging.info('\n%s \n' % seedvm_session.before)
            seedvm_session.sendline("cd " + seedvm_work_dir)
            seedvm_session.expect(seedvm_prompt)
            logging.info('\n%s \n' % seedvm_session.before)

        # upload qcow2 to "seedvm_work_dir"

        seedvm_cmd3 = "scp -r " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir + "/*.qcow2 " + "./"
        seedvm_session.sendline(seedvm_cmd3)
        seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=100)
        if seedvm_ret == 0:
            raise Exception("\nscp to webserver timeout \n")
        elif seedvm_ret == 1:
            seedvm_session.sendline(WEB_SERVER_PASSWORD)
        elif seedvm_ret == 2:
            logging.info('\n%s \n' % seedvm_session.before)
            seedvm_session.sendline("yes")
            seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=100)
            if seedvm_ret == 0:
                raise Exception("\nscp to webserver timeout \n")
            elif seedvm_ret == 1:
                logging.info('\n%s \n' % seedvm_session.before)
                seedvm_session.sendline(WEB_SERVER_PASSWORD)

        update_progbar_by_scp(user=user_found,
                              session=seedvm_session,
                              prompt=seedvm_prompt,
                              scp_step=3,
                              progbar_total_incr=35)

        ############## step3: Create Image
        logging.info('\nStep3: create image \n')
        seedvm_session.sendline("cd " + seedvm_work_dir)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        seedvm_session.sendline("source " + user_found.seedVMOpenrcAbsPath)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        create_glance_cmd = "glance image-create --name=" + select_pak.strip(".qcow2") + " --file=" + select_pak + \
                            " --disk-format=qcow2  --container-format=bare  --is-public=false --is-protected=false"
        logging.info('\n%s \n' % create_glance_cmd)
        seedvm_session.sendline(create_glance_cmd)
        seedvm_ret = seedvm_session.expect(['Errno', seedvm_prompt], timeout=50)
        if seedvm_ret == 0:
            logging.info('\n%s \n' % seedvm_session.before)
            raise Exception("\ncreate glance image failed \n")
        elif seedvm_ret ==1:
            logging.info('\n%s \n' % seedvm_session.before)

    except Exception, e:
        logging.error('\nproblem during ssh to seedvm server: %s \n' % str(e))
        user_found.progressBarData = "101"
        user_found.save()
        seedvm_session.close()
        return
