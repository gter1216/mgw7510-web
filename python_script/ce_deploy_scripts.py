from __future__ import division
from mgw7510.models import WebUser
from pexpect import pxssh
import ce_deploy_sub
import pexpect
import netcheck
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

# allowed minimal seed vm disk size, Gb
SEEDVM_DISK_LIMIT = "15"
WEB_SERVER_DISK_LIMIT = "200"

BUFFER_DIR = BASE_DIR + "/cache_dir/ce_deploy/qcow2_buffer_dir"
CACHE_DIR = BASE_DIR + "/cache_dir/ce_deploy/qcow2_cache_dir"

SEEDVM_WORK_DIR = "/root/auto_ce_deploy"
SEEDVM_BUFFER_dIR = SEEDVM_WORK_DIR + "/buffer_dir"
SEEDVM_CACHE_dIR = SEEDVM_WORK_DIR + "/cache_dir"

YACT_COMMON_TOOL_USER_DIR = BASE_DIR + "/YACT/UserDir"


def start_ce_deployment(uname, select_rel, select_pak):

    # ================ global var inital ================================
    user_found = WebUser.objects.get(username=uname)
    uname_dir = uname.replace("@", "_")
    work_dir = user_found.userWorkDir + "/ce_deploy_dir"
    user_upload_dir = work_dir + "/UserUploadDir"
    log_file = work_dir + "/ce_deploy.log"

    pak_server_info = {'ip': user_found.pakServerIp,
                       'username': user_found.pakServerUsername,
                       'passwd': user_found.pakServerPasswd,
                       "prompt": '\$',
                       "fp": user_found.pakServerFp}

    seedvm_info = {'ip': user_found.seedVMIp,
                   'username': user_found.seedVMUsername,
                   'passwd': user_found.seedVMPasswd,
                   'prompt': '#',
                   'openrc': user_found.seedVMOpenrcAbsPath,
                   'keypath': user_found.seedVMKeypairAbsPath,
                   'userdir': SEEDVM_WORK_DIR + "/" + uname_dir}

    yact_server_info = {'ip': user_found.yactServerIp,
                        'username': user_found.yactServerUsername,
                        'passwd': user_found.yactServerPasswd,
                        'prompt': '\$'}

    ce_deploy_sub.update_progress_bar(user_found, "1")

    qcow2_cached_seedvm_flag = False
    qcow2_cached_webserver_flag = False

    # ================ clean all the files under user_dir/ce_deploy_dir/UserUploadDir
    # ================ remove all old files in UserUploadDir
    user_upload_dir = work_dir + "/UserUploadDir"
    if os.path.isdir(user_upload_dir):
        shutil.rmtree(user_upload_dir)
        os.mkdir(user_upload_dir)

    # ================ initial log file ====================================

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S', filename=log_file, filemode='w')

    logging.info('\nstart ce deployment\n')

    logging.info('\n'
                 'Username is %s, \n'
                 'Release is %s, \n'
                 'Pak is %s \n' % (uname, select_rel, select_pak))

    logging.info('\npak server info: %s \n' % pak_server_info)
    logging.info('\nseedvm info: %s \n' % seedvm_info)
    logging.info('\nyact server info: %s \n' % yact_server_info)

    # ================ move user input file to user dir
    # ================ and get some parameters from user input

    user_input_file_name = user_found.userInputFileName

    # get user input file
    user_input_source = BASE_DIR + "/media/" + user_found.tmpPath + "/" + user_input_file_name
    user_input_target = user_upload_dir + '/' + user_input_file_name
    shutil.move(user_input_source, user_input_target)

    logging.info('\nuser uploaded file "%s" is ready to use \n\n' % user_input_file_name)

    parse_user_input_result = ce_deploy_sub.handle_user_input(user_input_target, uname_dir)

    if parse_user_input_result is None:
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return

    (sheet_name, system_name, sw_image_name, scm_ex_ip1, scm_ex_ip2, scm_oam_ip) = parse_user_input_result

    # ================ Environment Pre-Check Start =================
    logging.info('\nStep0: Environment Check Start!\n')

    # ==== (1) hosts connection check
    hosts_ip = {
        'pak server': pak_server_info['ip'],
        'seed vm': seedvm_info['ip'],
        'yact server': yact_server_info['ip']
    }

    env_check_result = netcheck.get_host_conn_state(hosts_ip)

    if env_check_result is False:
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return

    # ==== (2) evn pre check finish
    ce_deploy_sub.update_progress_bar(user_found, "3")
    logging.info('\nEnvironment Check Passed!\n')

    # ================ check qcow2 cache =================
    logging.info('\nStep1: check cached qcow2 on seedvm!\n')

    qcow2_md5 = ce_deploy_sub.get_qcow2_md5_from_pak(pak_server_info, select_pak, select_rel)

    logging.info('\nqcow2 md5 on pak is: %s \n' % qcow2_md5)

    if not qcow2_md5:
        # failed to get md5 on pak, ssh problem.
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return

    qcow2_cached_seedvm_flag = ce_deploy_sub.get_seedvm_qcow2_cached_flag_and_create_image(
        uname_dir, seedvm_info, select_pak, qcow2_md5, sw_image_name)

    if qcow2_cached_seedvm_flag is None:
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return
    elif qcow2_cached_seedvm_flag is not True:
        logging.info('\nStep2: check cached qcow2 on webserver!\n')
        # there is no cached qcow2 on seedvm, check if cached qcow2 exists on web server
        qcow2_cached_webserver_flag = ce_deploy_sub.get_webserver_qcow2_cached_flag(select_pak, qcow2_md5)
        if qcow2_cached_webserver_flag is None:
            ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
            return

    ce_deploy_sub.update_progress_bar(user_found, "5")

    logging.info('\nqcow2_cached_seedvm_flag is: %s, qcow2_cached_webserver_flag is: %s\n' %
                 (qcow2_cached_seedvm_flag, qcow2_cached_webserver_flag))

    if (qcow2_cached_seedvm_flag is False) and \
            (qcow2_cached_webserver_flag is False):
        logging.info('\nStep3: download qcow2 and csar to webserver from pakserver!\n')
        # no cache at all, perform download csar and qcow2 to webserver
        download_result = ce_deploy_sub.download_files_to_webserver(
            user_found, pak_server_info, select_rel, select_pak, user_upload_dir, True)
        if download_result is False:
            ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
            return

        ce_deploy_sub.update_progress_bar(user_found, "45")

        # upload qcow2 to webserver and create image,
        # and then move qcow2 from buffer to cache
        logging.info('\nStep4: upload qcow2 to seedvm and create image\n')
        upload_result = ce_deploy_sub.upload_qcow2_to_seed_create_image(
            user_found, seedvm_info, select_pak, sw_image_name)

        if upload_result is False:
            ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
            return

    elif (qcow2_cached_seedvm_flag is False) and \
            (qcow2_cached_webserver_flag is True):
        # perform download csar file only to webserver
        logging.info('\nStep3: no need to download qcow2, only download '
                     'csar to webserver from pakserver!\n')
        download_result = ce_deploy_sub.download_files_to_webserver(
            user_found, pak_server_info, select_rel, select_pak, user_upload_dir, False)

        if download_result is False:
            ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
            return

        ce_deploy_sub.update_progress_bar(user_found, "45")
        # upload qcow2 to webserver and create image, and then
        # and then move qcow2 from buffer to cache
        logging.info('\nStep4: upload qcow2 to seedvm and create image\n')
        upload_result = ce_deploy_sub.upload_qcow2_to_seed_create_image(
            user_found, seedvm_info, select_pak, uname_dir)

        if upload_result is False:
            ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
            return

    elif qcow2_cached_seedvm_flag is True:
        # perform download csar file only to webserver
        logging.info('\nStep3: no need to download qcow2, only download '
                     'csar to webserver from pakserver!\n')
        download_result = ce_deploy_sub.download_files_to_webserver(
            user_found, pak_server_info, select_rel, select_pak, user_upload_dir, False)

        if download_result is False:
            ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
            return

        # image created success
        ce_deploy_sub.update_progress_bar(user_found, "80")
        logging.info('\nStep4: cached qcow2 found on seedvm, create image successful\n')

    # ================ make yaml and scripts, replace csar =================
    logging.info('\nStep5: make yaml and scripts start\n')

    make_yaml_result = ce_deploy_sub.make_yaml_scripts(uname_dir, sheet_name)

    if make_yaml_result is False:
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return

    ce_deploy_sub.update_progress_bar(user_found, "85")
    logging.info('\n make yaml and scripts successful\n')

    # ================ replaced csar is ready, upload to seedvm =============
    logging.info('\nStep6: start to upload csar to seedvm\n')

    create_stack_result = ce_deploy_sub.create_stack(
        seedvm_info, user_upload_dir, system_name, scm_ex_ip1, scm_ex_ip2, scm_oam_ip)

    if create_stack_result is False:
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return

    # ================ all work finished ==================================
    ce_deploy_sub.deployment_success(user_found, perform_clean_work="no")
    return

# clear log_file
# log_file_cmd1 = "rm -rf %s" % log_file
# log_file_cmd2 = "touch %s" % log_file
# os.system(log_file_cmd1)
# os.system(log_file_cmd2)
#
# # wait enough time for the log file is touched.
# time.sleep(0.5)

# close
#
#     # updage progress bar to 5%
#     user_found.progressBarData = "5"
#     user_found.save()
#
#     #remove all old files in UserUploadDir
#     user_upload_dir = work_dir + "/UserUploadDir"
#     user_input_file_name = user_found.userInputFileName
#     ################## debug close ###########################
#     if os.path.isdir(user_upload_dir):
#         shutil.rmtree(user_upload_dir)
#         os.mkdir(user_upload_dir)
#     ################## debug close ###########################
#
#     # get user input file
#     user_input_source = BASE_DIR + "/media/" + user_found.tmpPath + "/" + user_input_file_name
#     user_input_target = user_upload_dir + '/' + user_input_file_name
#     shutil.move(user_input_source, user_input_target)
#
#     logging.info('\nuser uploaded file "%s" is ready to use \n\n' % user_input_file_name)
#















