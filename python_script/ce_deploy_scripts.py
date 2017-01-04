from mgw7510.models import WebUser
from pexpect import pxssh
import logging
import shutil
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

    user_found = WebUser.objects.get(username=uname)

    work_dir = user_found.userWorkDir + "/ce_deploy_dir/"

    # remove all files under work dir
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir)
        os.mkdir(work_dir)

    # create log file
    log_file = work_dir + '/ce_deploy.log'
    os.system(r'touch %s' % log_file)

    # initial log setting
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=log_file,
                        filemode='w')

    # updage progress bar to 2%
    user_found.progressBarData = "2"
    user_found.save()

    logging.info('start ce deployment')
    logging.info('log file ready')

    # log initial parameters for ce deployment
    logging.info('\n'
                 'Username is %s, \n'
                 'Release is %s, \n'
                 'Pak is %s \n'
                 % (uname, select_rel, select_pak)
                 )

    # get user input file
    user_input_source = BASE_DIR + "/media/" + user_found.tmpPath + "/" + user_found.userInputFileName
    user_input_target = work_dir + user_found.userInputFileName

    shutil.move(user_input_source, user_input_target)











