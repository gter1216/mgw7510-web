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
    log_file_cmd1 = "rm -rf %s" % log_file
    log_file_cmd2 = "touch %s" % log_file
    os.system(log_file_cmd1)
    os.system(log_file_cmd2)

    time.sleep(5)

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

    #remove old user input files
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

    return


    ###########################################################
    ##### first step:
    ###########################################################












