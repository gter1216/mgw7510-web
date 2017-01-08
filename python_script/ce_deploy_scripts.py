from __future__ import division
from mgw7510.models import WebUser
from pexpect import pxssh
import pexpect
import logging
import shutil
import time
import re
import os

# global var
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_SERVER_IP = "135.251.216.181"
WEB_SERVER_USERNAME = "root"
WEB_SERVER_PASSWORD = "newsys"
WEB_SERVER_PROMPT = '#'


# general function to ssh to the specific host
def createSSHSession(host, username, password, prompt):
    cmd = 'ssh ' + username + '@' + host

    logging.info('\n%s \n' % cmd)

    child = pexpect.spawn(cmd)
    ret = child.expect([pexpect.TIMEOUT, 'password:', 'Are you sure you want to continue connecting'], timeout=5)

    logging.info('\nret is %s \n' % ret)

    if ret == 0:
        raise Exception("\nssh to %s timeout \n" % host)
    elif ret == 1:
        child.sendline(password)
        child.expect(prompt)
    elif ret == 2:
        child.sendline("yes")
        ret = child.expect([pexpect.TIMEOUT, 'password'], timeout=5)
        if ret == 0:
            raise Exception("\nssh to %s timeout \n" % host)
        elif ret == 1:
            child.sendline(password)
            child.expect(prompt)

    # successful login to the host
    logging.info('\n%s \n' % child.before)
    return child




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


def update_progbar_by_scp(user, session, prompt, scp_step, progbar_total_incr):

    scp_list = range(1, 100, scp_step)
    scp_len = len(scp_list)

    progbar_step = round(progbar_total_incr/(scp_len+1))
    progbar_step = int(progbar_step)

    scp_to = round(360/(scp_len+1))
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

def start_ce_deployment(uname, select_rel, select_pak):

    # initial log setting
    user_found = WebUser.objects.get(username=uname)
    work_dir = user_found.userWorkDir + "/ce_deploy_dir"
    log_file = work_dir + "/ce_deploy.log"

    # clear log_file
    # log_file_cmd1 = "rm -rf %s" % log_file
    # log_file_cmd2 = "touch %s" % log_file
    # os.system(log_file_cmd1)
    # os.system(log_file_cmd2)
    #
    # # wait enough time for the log file is touched.
    # time.sleep(0.5)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=log_file,
                        filemode='w')

    logging.info('start ce deployment')
    logging.info('log file ready')

    # log initial parameters for ce deployment
    logging.info('\n'
                 'Username is %s, \n'
                 'Release is %s, \n'
                 'Pak is %s \n'
                 % (uname, select_rel, select_pak)
                 )

    # updage progress bar to 5%
    user_found.progressBarData = "5"
    user_found.save()

    #remove all old files in UserUploadDir
    user_upload_dir = work_dir + "/UserUploadDir"
    user_input_file_name = user_found.userInputFileName
    if os.path.isdir(user_upload_dir):
        shutil.rmtree(user_upload_dir)
        os.mkdir(user_upload_dir)

    # get user input file
    user_input_source = BASE_DIR + "/media/" + user_found.tmpPath + "/" + user_input_file_name
    user_input_target = user_upload_dir + '/' + user_input_file_name
    shutil.move(user_input_source, user_input_target)

    logging.info('\nuser uploaded file "%s" is ready to use \n\n' % user_input_file_name)

    #####################################################################################
    ##### step1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer START
    #####################################################################################
    logging.info('\nStep1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer \n')
    pak_server_ip = user_found.pakServerIp
    pak_server_username = user_found.pakServerUsername
    pak_server_password = user_found.pakServerPasswd
    pak_server_fp = user_found.pakServerFp

    logging.info('\n'
                 'pak server ip is %s, \n'
                 'pak server username is %s, \n'
                 'pak server password is is %s \n' % (pak_server_ip, pak_server_username, pak_server_password))

    # target path is ===> user_upload_dir

    # get source path
    # find ./ -name "nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2"
    # -exec bash -c 'scp -a `dirname {}` ./xuxiao ' \;
    # find /viewstores/public/SLP/7510C71 -name "nokia-mgw-rhel7.2-3.10.0-327.18.2-2.ae1b0416.x86_64.qcow2" -exec bash -c 'dirname {}' \;
    # /viewstores/public/SLP/7510C71/A7510_C71_11_04_2016_ae1b0416

    try:
        # $ is a special prompt, need add \
        # pak_prompt = [pexpect.TIMEOUT, '\$']
        pak_prompt = '\$'
        pak_session = createSSHSession(pak_server_ip, pak_server_username, pak_server_password, pak_prompt)

        # cd `find /viewstores/public/SLP/7510C71/ -name nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2 -exec dirname {} \;`
        pak_cmd = "cd " + "`" + "find " + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
                "-name " + select_pak + " -exec " + "dirname {} " + '\\;' + "`"

        pak_session.sendline(pak_cmd)
        pak_session.expect(pak_prompt)
        logging.info('\n%s \n' % pak_session.before)

        logging.info('\nls \n')
        pak_session.sendline('ls')
        pak_session.expect(pak_prompt)
        logging.info('\n%s \n' % pak_session.before)

        # scp -r *M_O*csar.zip *.qcow2 root@135.251.216.181:user_upload_dir

        pak_cmd2 = "scp -r " + "*M_O*csar.zip *.qcow2 " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir
        logging.info('\n%s \n' % pak_cmd2)
        pak_session.sendline(pak_cmd2)
        pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=5)
        if pak_ret == 0:
            raise Exception("\nscp to webserver timeout \n")
        elif pak_ret == 1:
            pak_session.sendline(WEB_SERVER_PASSWORD)
        elif pak_ret == 2:
            logging.info('\n%s \n' % pak_session.before)
            pak_session.sendline("yes")
            pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=5)
            if pak_ret == 0:
                raise Exception("\nscp to webserver timeout \n")
            elif pak_ret == 1:
                logging.info('\n%s \n' % pak_session.before)
                pak_session.sendline(WEB_SERVER_PASSWORD)

        update_progbar_by_scp(user=user_found,
                              session=pak_session,
                              prompt=pak_prompt,
                              scp_step=3,
                              progbar_total_incr=35)


        # pak_session.expect(pak_prompt, timeout=360)
        # pak_session.expect('10%', timeout=36)
        # user_found.progressBarData = "5"
        # user_found.save()
        #
        # pak_session.expect('20%', timeout=36)
        # user_found.progressBarData = "8"
        # user_found.save()
        #
        # pak_session.expect('30%', timeout=36)
        # user_found.progressBarData = "11"
        # user_found.save()
        #
        # pak_session.expect('40%', timeout=36)
        # user_found.progressBarData = "14"
        # user_found.save()
        #
        # pak_session.expect('50%', timeout=36)
        # user_found.progressBarData = "17"
        # user_found.save()
        #
        # pak_session.expect('60%', timeout=36)
        # user_found.progressBarData = "20"
        # user_found.save()
        #
        # pak_session.expect('70%', timeout=36)
        # user_found.progressBarData = "23"
        # user_found.save()
        #
        # pak_session.expect('80%', timeout=36)
        # user_found.progressBarData = "26"
        # user_found.save()
        #
        # pak_session.expect('90%', timeout=36)
        # user_found.progressBarData = "29"
        # user_found.save()
        #
        # pak_session.expect(pak_prompt, timeout=36)
        # user_found.progressBarData = "32"
        # user_found.save()

        # logging.info('\nssh to pak server \n')
        # s = pxssh.pxssh()
        # s.login(pak_server_ip, pak_server_username, pak_server_password, original_prompt='[$#>]')
        #
        #
        # # cd `find /viewstores/public/SLP/7510C71/ -name nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2 -exec dirname {} \;`
        #
        # cmd1 = "cd " + "`" + "find " + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
        #         "-name " + select_pak + " -exec " + "dirname {} " + '\\;' + "`"
        #
        # logging.info('\ncmd is: %s \n' % cmd1)
        # s.sendline(cmd1)
        # s.prompt()
        #
        # s.sendline('ls')
        # s.prompt()
        # logging.info('\nls is: %s \n' % s.before)
        #
        # # scp -r *M_O*csar.zip *.qcow2 root@135.251.216.181:user_upload_dir
        #
        # cmd2 = "scp -r " + "*M_O*csar.zip *.qcow2 " + "root@135.251.216.181:" + user_upload_dir
        # logging.info('\ncmd is: %s \n' % cmd2)
        # s.sendline(cmd2)
        # s.prompt()
        #
        # s.logout()

    except Exception, e:
        logging.error('\nproblem during ssh to pak server: %s \n' % str(e))
        user_found.progressBarData = "101"
        user_found.save()
        return
    finally:
        pak_session.close()

    #####################################################################################
    ##### step1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer END
    #####################################################################################






















