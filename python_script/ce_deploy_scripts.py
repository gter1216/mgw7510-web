from mgw7510.models import WebUser
from pexpect import pxssh
import logging
import shutil
import time
import re
import os

# global var
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def start_ce_deployment(uname, select_rel, select_pak):

    # initial log setting
    user_found = WebUser.objects.get(username=uname)
    work_dir = user_found.userWorkDir + "/ce_deploy_dir/"
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

    # updage progress bar to 2%
    user_found.progressBarData = "10"
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

    ###############################################################################
    ##### step1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer
    ################################################################################
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
        logging.info('\nssh to pak server \n')
        s = pxssh.pxssh()
        s.login(pak_server_ip, pak_server_username, pak_server_password, original_prompt='[$#>]')

        # cmd1 = 'find ' + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
        #        "-name " + select_pak + " -exec bash -c " + " 'dirname {}' " + '\\;'

        # cd `find /viewstores/public/SLP/7510C71/ -name nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2 -exec dirname {} \;`

        cmd1 = "cd " + "`" + "find " + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
                "-name " + select_pak + " -exec " + "dirname {} " + '\\;' + "`"

        logging.info('\ncmd is: %s \n' % cmd1)
        s.sendline(cmd1)
        s.prompt()

        s.sendline('ls')
        s.prompt()
        logging.info('\nls is: %s \n' % s.before)

        s.sendline('scp ')
        s.logout()


    except pxssh.ExceptionPxssh, e:
        # updage progress bar to 101%, failed
        logging.error('\nfailed ssh to pak server \n')
        user_found.progressBarData = "101"
        user_found.save()
        return






















