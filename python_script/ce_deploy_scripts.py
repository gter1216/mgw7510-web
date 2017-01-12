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


def start_ce_deployment(uname, select_rel, select_pak):

    # ================ global var
    user_found = WebUser.objects.get(username=uname)
    uname_dir = uname.replace("@", "_")
    work_dir = user_found.userWorkDir + "/ce_deploy_dir"
    log_file = work_dir + "/ce_deploy.log"

    pak_server_info = {'ip': user_found.pakServerIp,
                       'username': user_found.pakServerUsername,
                       'passwd': user_found.pakServerPasswd,
                       "fp": user_found.pakServerFp}

    seedvm_info = {'ip': user_found.seedVMIp,
                   'username': user_found.seedVMUsername,
                   'passwd': user_found.seedVMPasswd,
                   'work_dir': "/root/" + uname_dir}

    yact_server_info = {'ip': user_found.yactServerIp,
                        'username': user_found.yactServerUsername,
                        'passwd': user_found.yactServerPasswd}

    # ================ initial data
    ce_deploy_sub.update_progress_bar(user_found, "1")

    # ================ initial log file
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S', filename=log_file, filemode='w')

    logging.info('\nstart ce deployment\n')

    logging.info('\n'
                 'Username is %s, \n'
                 'Release is %s, \n'
                 'Pak is %s \n' % (uname, select_rel, select_pak))

    # ================ Step 0: Environment Pre-Check Start ===================
    logging.info('\nStep0: Environment Check Start!\n')

    hosts_ip = {
        'pak server': pak_server_info['ip'],
        'seed vm': seedvm_info['ip'],
        'yact server': yact_server_info['ip']
    }

    env_check_result = netcheck.get_host_conn_state(hosts_ip)

    if env_check_result is False:
        logging.info('\nEnvironment Check Failed!\n')
        ce_deploy_sub.deployment_failed(user_found, perform_clean_work="no")
        return

    ce_deploy_sub.update_progress_bar(user_found, "3")
    logging.info('\nEnvironment Check Passed!\n')

    # ================ Step 0: Environment Pre-Check End ===================

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
#     #####################################################################################
#     ##### step1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer START
#     #####################################################################################
#     # for debug mode only, start
#     logging.info('\nStep1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer \n')

#
#     logging.info('\n'
#                  'pak server ip is %s, \n'
#                  'pak server username is %s, \n'
#                  'pak server password is is %s \n' % (pak_server_ip, pak_server_username, pak_server_password))
#
#     # target path is ===> user_upload_dir
#
#     # get source path
#     # find ./ -name "nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2"
#     # -exec bash -c 'scp -a `dirname {}` ./xuxiao ' \;
#     # find /viewstores/public/SLP/7510C71 -name "nokia-mgw-rhel7.2-3.10.0-327.18.2-2.ae1b0416.x86_64.qcow2" -exec bash -c 'dirname {}' \;
#     # /viewstores/public/SLP/7510C71/A7510_C71_11_04_2016_ae1b0416
#
#     try:
#         # $ is a special prompt, need add \
#         # pak_prompt = [pexpect.TIMEOUT, '\$']
#         pak_prompt = '\$'
#         pak_session = createSSHSession(pak_server_ip, pak_server_username, pak_server_password, pak_prompt)
#
#         # cd `find /viewstores/public/SLP/7510C71/ -name nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2 -exec dirname {} \;`
#         pak_cmd = "cd " + "`" + "find " + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
#                 "-name " + select_pak + " -exec " + "dirname {} " + '\\;' + "`"
#
#         pak_session.sendline(pak_cmd)
#         pak_session.expect(pak_prompt)
#         logging.info('\n%s \n' % pak_session.before)
#
#         logging.info('\nls \n')
#         pak_session.sendline('ls')
#         pak_session.expect(pak_prompt)
#         logging.info('\n%s \n' % pak_session.before)
#
#         # scp -r *M_O*csar.zip *.qcow2 root@135.251.216.181:user_upload_dir
#
#         pak_cmd2 = "scp -r " + "*M_O*csar.zip *.qcow2 " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir
#         # pak_cmd2 = "scp -r " + "*M_O*csar.zip " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir
#
#
#         logging.info('\n%s \n' % pak_cmd2)
#         pak_session.sendline(pak_cmd2)
#         pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=5)
#         if pak_ret == 0:
#             raise Exception("\nscp to webserver timeout \n")
#         elif pak_ret == 1:
#             pak_session.sendline(WEB_SERVER_PASSWORD)
#         elif pak_ret == 2:
#             logging.info('\n%s \n' % pak_session.before)
#             pak_session.sendline("yes")
#             pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=5)
#             if pak_ret == 0:
#                 raise Exception("\nscp to webserver timeout \n")
#             elif pak_ret == 1:
#                 logging.info('\n%s \n' % pak_session.before)
#                 pak_session.sendline(WEB_SERVER_PASSWORD)
#
#         update_progbar_by_scp(user=user_found,
#                               session=pak_session,
#                               prompt=pak_prompt,
#                               scp_step=3,
#                               progbar_total_incr=35)
#
#     except Exception, e:
#         logging.error('\nproblem during ssh to pak server: %s \n' % str(e))
#         user_found.progressBarData = "101"
#         user_found.save()
#         pak_session.close()
#         return
#     pak_session.close()
#     # for debug mode only, end
#     #####################################################################################
#     ##### step1: Get CSAR & QCOW2 file from PakServer(ngnsvr11) into WebServer END
#     #####################################################################################
#
#
#
#     #####################################################################################
#     ##### step2: Upload QCOW2 file into SeedVM START
#     #####################################################################################
#     # for debug mode only, start
#     logging.info('\nStep2: Upload QCOW2 file into SeedVM \n')
#
#     logging.info('\n'
#                  'seed vm ip is %s, \n'
#                  'seed vm username is %s, \n'
#                  'seed vm password is is %s \n' % (seedvm_ip, seedvm_username, seedvm_passwd))
#
#     try:
#         seedvm_prompt = '#'
#         seedvm_session = createSSHSession(seedvm_ip, seedvm_username, seedvm_passwd, seedvm_prompt)
#
#
#         # create seed vm workdir
#         # if exists, then rm it and then create it
#         seedvm_cmd = "mkdir " + seedvm_work_dir
#         seedvm_session.sendline(seedvm_cmd)
#         seedvm_ret = seedvm_session.expect([seedvm_prompt, 'File exists'])
#
#         if seedvm_ret == 0:
#             logging.info('\n%s \n' % seedvm_session.before)
#         elif seedvm_ret == 1:
#             # first match File exists, then match '~#' !!!!!!!!!!IMPORTANT!!!!!!!!!!
#             seedvm_session.expect(seedvm_prompt)
#             logging.info('\n%s \n' % seedvm_session.before)
#             seedvm_session.sendline("rm -rf " + seedvm_work_dir)
#             seedvm_session.expect(seedvm_prompt)
#             logging.info('\n%s \n' % seedvm_session.before)
#             seedvm_session.sendline(seedvm_cmd)
#             seedvm_session.expect(seedvm_prompt)
#             logging.info('\n%s \n' % seedvm_session.before)
#             seedvm_session.sendline("cd " + seedvm_work_dir)
#             seedvm_session.expect(seedvm_prompt)
#             logging.info('\n%s \n' % seedvm_session.before)
#
#         # upload qcow2 to "seedvm_work_dir"
#
#         seedvm_cmd3 = "scp -r " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir + "/*.qcow2 " + "./"
#         seedvm_session.sendline(seedvm_cmd3)
#         seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=100)
#         if seedvm_ret == 0:
#             raise Exception("\nscp to webserver timeout \n")
#         elif seedvm_ret == 1:
#             seedvm_session.sendline(WEB_SERVER_PASSWORD)
#         elif seedvm_ret == 2:
#             logging.info('\n%s \n' % seedvm_session.before)
#             seedvm_session.sendline("yes")
#             seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=100)
#             if seedvm_ret == 0:
#                 raise Exception("\nscp to webserver timeout \n")
#             elif seedvm_ret == 1:
#                 logging.info('\n%s \n' % seedvm_session.before)
#                 seedvm_session.sendline(WEB_SERVER_PASSWORD)
#
#         update_progbar_by_scp(user=user_found,
#                               session=seedvm_session,
#                               prompt=seedvm_prompt,
#                               scp_step=3,
#                               progbar_total_incr=35)
#
#         ############## step3: Create Image
#         logging.info('\nStep3: create image \n')
#         seedvm_session.sendline("cd " + seedvm_work_dir)
#         seedvm_session.expect(seedvm_prompt)
#         logging.info('\n%s \n' % seedvm_session.before)
#
#         seedvm_session.sendline("source " + user_found.seedVMOpenrcAbsPath)
#         seedvm_session.expect(seedvm_prompt)
#         logging.info('\n%s \n' % seedvm_session.before)
#
#         create_glance_cmd = "glance image-create --name=" + select_pak.strip(".qcow2") + " --file=" + select_pak + \
#                             " --disk-format=qcow2  --container-format=bare  --is-public=false --is-protected=false"
#         logging.info('\n%s \n' % create_glance_cmd)
#         seedvm_session.sendline(create_glance_cmd)
#         seedvm_ret = seedvm_session.expect(['Errno', seedvm_prompt], timeout=50)
#         if seedvm_ret == 0:
#             logging.info('\n%s \n' % seedvm_session.before)
#             raise Exception("\ncreate glance image failed \n")
#         elif seedvm_ret ==1:
#             logging.info('\n%s \n' % seedvm_session.before)
#
#     except Exception, e:
#         logging.error('\nproblem during ssh to seedvm server: %s \n' % str(e))
#         user_found.progressBarData = "101"
#         user_found.save()
#         seedvm_session.close()
#         return
#
#     seedvm_session.close()
#     # for debug only, stop
#
#     user_found.progressBarData = "80"
#     user_found.save()
#
#     #####################################################################################
#     ##### step2,3: Upload CSAR & QCOW2 file into SeedVM & Create Image END
#     #####################################################################################
#
#
#     #####################################################################################
#     ##### step4: Make YAML & SCRIPT files Start, then download ne_xxx to webserver
#     #####################################################################################
#     # for debug close
#     logging.info('\nStep4: Make YAML & SCRIPT Files on YACT Server, thend download to webserver \n')

#
#     logging.info('\n'
#                  'yact server ip is %s, \n'
#                  'yact server username is %s, \n'
#                  'yact server password is is %s \n'
#                  'yact server dif tool path is %s\n'
#                  'yact server yact tool path is %s\n'
#                  % (yact_server_ip,
#                     yact_server_username,
#                     yact_server_passwd,
#                     yact_server_dif_path,
#                     yact_server_yact_path))
#
#     try:
#         yact_prompt = '\$'
#         yact_session = createSSHSession(yact_server_ip, yact_server_username, yact_server_passwd, yact_prompt)
#
#         # rename the user input file
#         new_user_input_file_name = uname_dir + '_' + user_input_file_name
#         new_user_input_source = user_input_target
#         new_user_input_target = user_upload_dir + '/' + new_user_input_file_name
#         shutil.move(new_user_input_source, new_user_input_target)
#
#         # upload user input to yact server dif path
#         yact_session.sendline("cd " + yact_server_dif_path)
#         yact_session.expect(yact_prompt)
#         logging.info('\n%s \n' % yact_session.before)
#
#         yact_scp_cmd = "scp -r " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + new_user_input_target + " ./"
#         yact_session.sendline(yact_scp_cmd)
#         yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=50)
#         if yact_ret == 0:
#             raise Exception("\nscp to webserver timeout \n")
#         elif yact_ret == 1:
#             yact_session.sendline(WEB_SERVER_PASSWORD)
#         elif yact_ret == 2:
#             logging.info('\n%s \n' % yact_session.before)
#             yact_session.sendline("yes")
#             yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=50)
#             if yact_ret == 0:
#                 raise Exception("\nscp to webserver timeout \n")
#             elif yact_ret == 1:
#                 logging.info('\n%s \n' % yact_session.before)
#                 yact_session.sendline(WEB_SERVER_PASSWORD)
#
#         yact_session.expect(yact_prompt)
#         logging.info('\n%s \n' % yact_session.before)
#
#         user_found.progressBarData = "82"
#         user_found.save()
#
#         # generate output by DIF tool
#         # python dif_fill.py -i input-dif.xlsm -u user-input-xuxiao.xlsx -o output-xuxiao.xlsm
#         # cp output-xuxiao.xlsm  /home/darcy/YACT/
#
#         yact_output_name = "output_" + new_user_input_file_name.strip("xlsx") + "xlsm"
#         yact_gen_output_cmd = "python dif_fill.py -i input-dif.xlsm -u " + \
#                               new_user_input_file_name + " -o " + yact_output_name
#
#         logging.info('\n%s \n' % yact_gen_output_cmd)
#
#         yact_session.sendline(yact_gen_output_cmd)
#         yact_session.expect(yact_prompt, timeout=300)
#         logging.info('\n%s \n' % yact_session.before)
#
#         yact_session.sendline("mv " + yact_output_name + " " + yact_server_yact_path)
#         yact_session.expect(yact_prompt)
#         logging.info('\n%s \n' % yact_session.before)
#
#         # remove uploaded user input file
#         yact_session.sendline("rm -rf " + new_user_input_file_name)
#         yact_session.expect(yact_prompt)
#         logging.info('\n%s \n' % yact_session.before)
#
#         user_found.progressBarData = "84"
#         user_found.save()
#
#         # generate ne_xxx  YAML & SCRIPTS
#         yact_session.sendline("cd " + yact_server_yact_path)
#         yact_session.expect(yact_prompt)
#         logging.info('\n%s \n' % yact_session.before)
#
#         # ./yact.sh gen-by-dif output-xuxiao.xlsm 7510-CE C710.ad1115
#         yact_yaml_cmd = "./yact.sh " + "gen-by-dif " + yact_output_name + " 7510-CE C710.ad1115"
#         yact_session.sendline(yact_yaml_cmd)
#         yact_session.expect(yact_prompt, timeout=100)
#         logging.info('\n%s \n' % yact_session.before)
#
#         # delete output xlsm file
#         yact_session.sendline("rm -rf " + yact_output_name)
#         yact_session.expect(yact_prompt)
#         logging.info('\n%s \n' % yact_session.before)
#
#         # download ne_xxx to user_upload_dir
#         yact_scp_cmd = "scp -r " + "./ne-xxx/ " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir
#         yact_session.sendline(yact_scp_cmd)
#         yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=5)
#         if yact_ret == 0:
#             raise Exception("\nscp to webserver timeout \n")
#         elif yact_ret == 1:
#             yact_session.sendline(WEB_SERVER_PASSWORD)
#         elif yact_ret == 2:
#             logging.info('\n%s \n' % yact_session.before)
#             yact_session.sendline("yes")
#             yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=5)
#             if yact_ret == 0:
#                 raise Exception("\nscp to webserver timeout \n")
#             elif yact_ret == 1:
#                 logging.info('\n%s \n' % yact_session.before)
#                 yact_session.sendline(WEB_SERVER_PASSWORD)
#
#         yact_session.expect(yact_prompt, timeout=200)
#         logging.info('\n%s \n' % yact_session.before)
#
#     except Exception, e:
#         logging.error('\nproblem during ssh to yact server: %s \n' % str(e))
#         user_found.progressBarData = "101"
#         user_found.save()
#         yact_session.close()
#         return
#     yact_session.close()
#     # for debug only, stop
#     # for debug close
#
#     user_found.progressBarData = "85"
#     user_found.save()
#
#     #####################################################################################
#     ##### step4: Make YAML & SCRIPT files End
#     #####################################################################################
#
#
#     #######################################################################################
#     ##### step5: Unzip CSAR, Replace YAML & SCRIPT files, then upload CSAR to seedvm START
#     #######################################################################################
#     logging.info('\nStep5: unzip CSAR, replace YAML & SCRIPT files, then upload CSAR to seedvm \n')
#
#     shell_file_path = BASE_DIR + "/shell_script/web_server_csar_handle.sh"
#     shell_cmd = "sh " + shell_file_path + " " + user_upload_dir + " >> " + log_file
#     os.system(shell_cmd)
#
#     # start upload nokia*.csar to  seedvm_work_dir = "/root/" + uname_dir
#
#     try:
#         seedvm_prompt = '#'
#         seedvm_session = createSSHSession(seedvm_ip, seedvm_username, seedvm_passwd, seedvm_prompt)
#
#         # for debug close
#         seedvm_cmd4 = "scp -r " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + \
#                       user_upload_dir + "/nokia*.csar " + seedvm_work_dir
#
#         logging.info('\n%s \n' % seedvm_cmd4)
#
#         seedvm_session.sendline(seedvm_cmd4)
#         seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=300)
#
#         if seedvm_ret == 0:
#             raise Exception("\nscp to webserver timeout \n")
#         elif seedvm_ret == 1:
#             seedvm_session.sendline(WEB_SERVER_PASSWORD)
#         elif seedvm_ret == 2:
#             logging.info('\n%s \n' % seedvm_session.before)
#             seedvm_session.sendline("yes")
#             seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=300)
#             if seedvm_ret == 0:
#                 raise Exception("\nscp to webserver timeout \n")
#             elif seedvm_ret == 1:
#                 logging.info('\n%s \n' % seedvm_session.before)
#                 seedvm_session.sendline(WEB_SERVER_PASSWORD)
#
#         seedvm_session.expect(seedvm_prompt, timeout=300)
#         logging.info('\n%s \n' % seedvm_session.before)
#
#         user_found.progressBarData = "86"
#         user_found.save()
#
#         ##### step6: generate hot and env files
#         logging.info('\nStep6: generate hot and env files \n')
#
#         seedvm_session.sendline("cd " + seedvm_work_dir + "/nokia*.csar/scripts")
#         seedvm_session.expect(seedvm_prompt)
#         logging.info('\n%s \n' % seedvm_session.before)
#
#         # ./template.py -a deploy -r cloud_config/cloud-resource-data.yaml
#         seedvm_session.sendline("./template.py -a deploy -r cloud_config/cloud-resource-data.yaml")
#         seedvm_session.expect(seedvm_prompt)
#
#         # get heat create command
#         cmd_result = seedvm_session.before
#         logging.info('\n%s \n' % cmd_result)
#         cmd_result = re.findall(r'heat.*\r', cmd_result)
#         create_heat_cmd = cmd_result[0].strip('\r')
#         logging.info('\n%s \n' % create_heat_cmd)
#
#         ##### step7: create 7510 stack
#         seedvm_session.sendline("source " + user_found.seedVMOpenrcAbsPath)
#         seedvm_session.expect(seedvm_prompt)
#         logging.info('\n%s \n' % seedvm_session.before)
#
#         logging.info('\nStep7: create 7510 stack \n')
#         seedvm_session.sendline(create_heat_cmd)
#         seedvm_session.expect(seedvm_prompt, timeout=300)
#         logging.info('\n%s \n' % seedvm_session.before)
#
#         # for debug close
#
#         # TBD
#         # # ##### step8: generate particular file "UUID.TXT"
#         # logging.info('\nStep8: generate particular file UUID.TXT \n')
#         #
#         # ##### step9: put needed files to v7510
#         # logging.info('\nStep9: put needed files to v7510 \n')
#         #
#         # ##### step10: run instal script on v7510
#         # logging.info('\nStep10: run instal script on v7510 \n')
#
#     except Exception, e:
#         logging.error('\nproblem during ssh to seedvm server: %s \n' % str(e))
#         user_found.progressBarData = "101"
#         user_found.save()
#         return
#     finally:
#         seedvm_session.close()
#     # for debug only, stop
#
#     logging.info('\nSuccessful Finished \n')
#     user_found.progressBarData = "100"
#     user_found.save()
















