from __future__ import division
from mgw7510.models import WebUser
from pexpect import pxssh
import ce_deploy_scripts
import commands
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


def update_progbar_by_scp(user, session, prompt, timer, progbar_total_incr):

    inc = float(progbar_total_incr) / 100

    session.expect("1%")
    logging.info('\n%s \n' % session.before)

    final_result_prev = 0
    initial_progress = int(user.progressBarData)

    while True:
        time.sleep(timer)
        session.expect("%")
        result1 = session.before
        result2 = result1.split()
        result3 = result2[5]
        final_result_second = int((int(result3)) * inc)
        if final_result_second > final_result_prev:
            logging.info('\n%s%%\n' % result1)
            user.progressBarData = str(initial_progress + final_result_second)
            user.save()
            final_result_prev = final_result_second
        if result3 == "100":
            session.expect(prompt)
            break

    logging.info('\n%s \n' % session.before)


# def update_progbar_by_scp(user, session, prompt, scp_step, progbar_total_incr):
#
#     scp_list = range(1, 100, scp_step)
#     scp_len = len(scp_list)
#
#     progbar_step = round(progbar_total_incr/(scp_len+1))
#     progbar_step = int(progbar_step)
#
#     scp_to = round(3600/(scp_len+1))
#     scp_to = int(scp_to)
#
#     # [1, 4, ... , 97]
#     for i_scp in scp_list:
#         scp_exp = str(i_scp)+"%"
#         session.expect(scp_exp, timeout=scp_to)
#         logging.info('\n%s \n' % session.before)
#         user.progressBarData = str(int(user.progressBarData) + progbar_step)
#         user.save()
#
#     session.expect(prompt, timeout=scp_to)
#     logging.info('\n%s \n' % session.before)
#     user.progressBarData = str(int(user.progressBarData) + progbar_step)
#     user.save()


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


def get_seedvm_qcow2_cached_flag_and_create_image(uname_dir, seedvm_info, qcow2_name, qcow2_md5):
    try:
        seedvm_ip = seedvm_info["ip"]
        seedvm_username = seedvm_info["username"]
        seedvm_passwd = seedvm_info["passwd"]
        seedvm_prompt = seedvm_info["prompt"]

        seedvm_session = create_ssh_session(seedvm_ip, seedvm_username, seedvm_passwd, seedvm_prompt)

        # upload script seedvm_cache_check.sh to seedvm /root/
        sh_file_path = ce_deploy_scripts.BASE_DIR + "/shell_script/seedvm_cache_check.sh"
        seedvm_scp_cmd = "scp -r " + ce_deploy_scripts.WEB_SERVER_USERNAME + "@" + \
                         ce_deploy_scripts.WEB_SERVER_IP + ":" + sh_file_path + " /root/"
        seedvm_session.sendline(seedvm_scp_cmd)
        seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=100)
        if seedvm_ret == 0:
            raise Exception("\nscp to webserver timeout \n")
        elif seedvm_ret == 1:
            seedvm_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)
        elif seedvm_ret == 2:
            logging.info('\n%s \n' % seedvm_session.before)
            seedvm_session.sendline("yes")
            seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=100)
            if seedvm_ret == 0:
                raise Exception("\nscp to webserver timeout \n")
            elif seedvm_ret == 1:
                logging.info('\n%s \n' % seedvm_session.before)
                seedvm_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        # perform shell script
        # $1 ===> /root/auto_ce_deploy
        # $2 ===> qcow2_name: nokia_a.qcow2
        # $3 ===> qcow2_md5: d41d8cd98f00b204e9800998ecf8427e
        # $4 ===> disk_limit: 15
        # $5 ===> source_file: /root/cloud-env/Rainbow-openrc.sh
        seedvm_cmd = "sh /root/seedvm_cache_check.sh " + "/root/auto_ce_deploy " + qcow2_name + " " + \
                     qcow2_md5 + " " + ce_deploy_scripts.SEEDVM_DISK_LIMIT + " " + seedvm_info["openrc"] + \
                     " " + uname_dir
        seedvm_session.sendline(seedvm_cmd)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)
        seedvm_cmd = "echo $?"
        seedvm_session.sendline(seedvm_cmd)
        seedvm_session.expect(seedvm_prompt)
        result = seedvm_session.before
        logging.info('\n%s \n' % result)
        exitcode = result.split("\r\n")
        exitcode = exitcode[1]
        logging.info('\n exit code is: %s \n' % exitcode)

        # remove shell script
        seedvm_cmd = "rm -rf /root/seedvm_cache_check.sh"
        seedvm_session.sendline(seedvm_cmd)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        seedvm_session.close()

        exitcode = int(exitcode)
        if exitcode == 1:
            logging.info('\nno cached qcow2 found on seedvm \n')
            return False
        elif exitcode == 2:
            logging.error('\nno enough disk storage on seedvm, please check! \n')
            return None
        elif exitcode == 3:
            logging.error('\ncreate image failed, please check! \n')
            return None
        elif exitcode == 4:
            logging.info('\nfind cached qcow2 on seedvm \n')
            return True
        else:
            logging.error('\nunkown error \n')
            return None

    except Exception, e:
        logging.error('\nproblem during ssh to seedvm server: %s \n' % str(e))
        return None


def get_webserver_qcow2_cached_flag(qcow2_name, qcow2_md5):
    shell_file_path = ce_deploy_scripts.BASE_DIR + "/shell_script/webserver_cache_check.sh"

    ce_deploy_dir = ce_deploy_scripts.BASE_DIR + "/cache_dir/ce_deploy"

    shell_cmd = "sh " + shell_file_path + " " + ce_deploy_dir + " " + \
                qcow2_name + " " + qcow2_md5 + " " + ce_deploy_scripts.WEB_SERVER_DISK_LIMIT

    logging.info('\n%s\n' % shell_cmd)

    output = commands.getstatusoutput(shell_cmd)
    exitcode = (output[0]) >> 8
    logging.info('\n%s\n' % exitcode)
    logging.info('\n%s\n' % output[1])

    if exitcode == 1:
        logging.info('\nno cached qcow2 found on webserver \n')
        return False
    elif exitcode == 2:
        logging.error('\nno enough disk storage on webserver, please check! \n')
        return None
    elif exitcode == 3:
        logging.info('\nfind cached qcow2 on seedvm \n')
        return True
    else:
        logging.error('\nunkown error \n')
        return None


def download_files_to_webserver(user, pak_server_info, select_rel, select_pak, user_upload_dir, both_flag):
    try:
        pak_server_ip = pak_server_info["ip"]
        pak_server_username = pak_server_info["username"]
        pak_server_password = pak_server_info["passwd"]
        pak_server_fp = pak_server_info["fp"]
        pak_prompt = pak_server_info["prompt"]

        pak_session = create_ssh_session(pak_server_ip, pak_server_username, pak_server_password, pak_prompt)

        # cd `find /viewstores/public/SLP/7510C71/ -name
        # nokia-mgw-rhel7.2-3.10.0-327.18.2.ae1a3116.x86_64.qcow2 -exec dirname {} \;`
        pak_cmd = "cd " + "`" + "find " + pak_server_fp + "/" + "7510" + select_rel.replace(".", "") + "/ " + \
                  "-name " + select_pak + " -exec " + "dirname {} " + '\\;' + "`"

        pak_session.sendline(pak_cmd)
        pak_session.expect(pak_prompt)
        logging.info('\n%s \n' % pak_session.before)

        logging.info('\nls \n')
        pak_session.sendline('ls')
        pak_session.expect(pak_prompt)
        logging.info('\n%s \n' % pak_session.before)

        if both_flag is True:
            # scp -r *M_O*csar.zip *.qcow2 root@135.251.216.181:user_upload_dir
            pak_cmd_qcow2 = "scp -r " + "*.qcow2 " + ce_deploy_scripts.WEB_SERVER_USERNAME + "@" + \
                            ce_deploy_scripts.WEB_SERVER_IP + ":" + ce_deploy_scripts.BUFFER_DIR
            logging.info('\n%s \n' % pak_cmd_qcow2)
            pak_session.sendline(pak_cmd_qcow2)
            pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=5)
            if pak_ret == 0:
                raise Exception("\nscp to webserver timeout \n")
            elif pak_ret == 1:
                pak_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)
            elif pak_ret == 2:
                logging.info('\n%s \n' % pak_session.before)
                pak_session.sendline("yes")
                pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=5)
                if pak_ret == 0:
                    raise Exception("\nscp to webserver timeout \n")
                elif pak_ret == 1:
                    logging.info('\n%s \n' % pak_session.before)
                    pak_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)

            update_progbar_by_scp(user=user, session=pak_session, prompt=pak_prompt,
                                  timer=0.1, progbar_total_incr=35)

            # download csar and qcow2 successfull
            # move qcow2 from buffer dir to cache dir
            shutil.move(ce_deploy_scripts.BUFFER_DIR + "/" + select_pak,
                        ce_deploy_scripts.CACHE_DIR + "/" + select_pak)

        pak_cmd_csar = "scp -r " + "*M_O*csar.zip yact-C* yact-nokia-mgw* " + ce_deploy_scripts.WEB_SERVER_USERNAME + "@" + \
                       ce_deploy_scripts.WEB_SERVER_IP + ":" + user_upload_dir

        logging.info('\n%s \n' % pak_cmd_csar)
        pak_session.sendline(pak_cmd_csar)
        pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=5)
        if pak_ret == 0:
            raise Exception("\nscp to webserver timeout \n")
        elif pak_ret == 1:
            pak_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)
        elif pak_ret == 2:
            logging.info('\n%s \n' % pak_session.before)
            pak_session.sendline("yes")
            pak_ret = pak_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=5)
            if pak_ret == 0:
                raise Exception("\nscp to webserver timeout \n")
            elif pak_ret == 1:
                logging.info('\n%s \n' % pak_session.before)
                pak_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)
        pak_session.expect(pak_prompt)
        logging.info('\n%s \n' % pak_session.before)
        pak_session.close()
        return True

    except Exception, e:
        logging.error('\nproblem during ssh to pak server: %s \n' % str(e))
        return False


def upload_qcow2_to_seed_create_image(user, seedvm_info, select_pak, uname_dir):
    try:
        seedvm_ip = seedvm_info["ip"]
        seedvm_username = seedvm_info["username"]
        seedvm_passwd = seedvm_info["passwd"]
        seedvm_prompt = seedvm_info["prompt"]
        seedvm_openrc = seedvm_info["openrc"]

        seedvm_session = create_ssh_session(seedvm_ip, seedvm_username, seedvm_passwd, seedvm_prompt)

        # upload qcow2 to buffer dir

        seedvm_cmd_scp = "scp -r " + ce_deploy_scripts.WEB_SERVER_USERNAME + "@" + \
                         ce_deploy_scripts.WEB_SERVER_IP + ":" + ce_deploy_scripts.CACHE_DIR + "/" + \
                         select_pak + " " + ce_deploy_scripts.SEEDVM_BUFFER_dIR

        logging.info('\n%s \n' % seedvm_cmd_scp)

        seedvm_session.sendline(seedvm_cmd_scp)

        seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=100)
        if seedvm_ret == 0:
            raise Exception("\nscp to webserver timeout \n")
        elif seedvm_ret == 1:
            seedvm_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)
        elif seedvm_ret == 2:
            logging.info('\n%s \n' % seedvm_session.before)
            seedvm_session.sendline("yes")
            seedvm_ret = seedvm_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=100)
            if seedvm_ret == 0:
                raise Exception("\nscp to webserver timeout \n")
            elif seedvm_ret == 1:
                logging.info('\n%s \n' % seedvm_session.before)
                seedvm_session.sendline(ce_deploy_scripts.WEB_SERVER_PASSWORD)

        update_progbar_by_scp(user=user,
                              session=seedvm_session,
                              prompt=seedvm_prompt,
                              timer=0.1,
                              progbar_total_incr=35)

        # ================= Create Image
        logging.info('\ncreate image \n')
        seedvm_session.sendline("cd " + ce_deploy_scripts.SEEDVM_BUFFER_dIR)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        seedvm_session.sendline("source " + seedvm_openrc)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        glance_name = select_pak.strip(".qcow2") + "_auto_" + uname_dir

        create_glance_cmd = "glance image-create --name=" + glance_name + " --file=" + select_pak + \
                            " --disk-format=qcow2  --container-format=bare  --is-public=false --is-protected=false"
        logging.info('\n%s \n' % create_glance_cmd)
        seedvm_session.sendline(create_glance_cmd)
        seedvm_ret = seedvm_session.expect(['Errno', seedvm_prompt], timeout=50)
        if seedvm_ret == 0:
            logging.info('\n%s \n' % seedvm_session.before)
            raise Exception("\ncreate glance image failed \n")
        elif seedvm_ret == 1:
            logging.info('\n%s \n' % seedvm_session.before)

        logging.info('\nmove qcow2 from buffer to cache, on seedvm \n')
        move_cmd = "mv " + ce_deploy_scripts.SEEDVM_BUFFER_dIR + "/" + select_pak + \
                   " " + ce_deploy_scripts.SEEDVM_CACHE_dIR + "/" + select_pak
        logging.info('\n%s \n' % move_cmd)
        seedvm_session.sendline(move_cmd)
        seedvm_session.expect(seedvm_prompt)
        logging.info('\n%s \n' % seedvm_session.before)

        logging.info('\ncreate glance image successful \n')
        seedvm_session.close()
        return True

    except Exception, e:
        logging.error('\nproblem during ssh to seedvm server: %s \n' % str(e))
        return False


def make_yaml_scripts(yact_server_info, user_input_file_name, user_upload_dir):
    try:
        yact_server_ip = yact_server_info["ip"]
        yact_server_username = yact_server_info["username"]
        yact_server_passwd = yact_server_info["passwd"]
        yact_prompt = yact_server_info["prompt"]

        yact_session = create_ssh_session(yact_server_ip, yact_server_username, yact_server_passwd, yact_prompt)

        yact_session.close()

        # yact_scp_cmd = "scp -r " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + new_user_input_target + " ./"
        # yact_session.sendline(yact_scp_cmd)
        # yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=50)
        # if yact_ret == 0:
        #     raise Exception("\nscp to webserver timeout \n")
        # elif yact_ret == 1:
        #     yact_session.sendline(WEB_SERVER_PASSWORD)
        # elif yact_ret == 2:
        #     logging.info('\n%s \n' % yact_session.before)
        #     yact_session.sendline("yes")
        #     yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=50)
        #     if yact_ret == 0:
        #         raise Exception("\nscp to webserver timeout \n")
        #     elif yact_ret == 1:
        #         logging.info('\n%s \n' % yact_session.before)
        #         yact_session.sendline(WEB_SERVER_PASSWORD)
        #
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)

        # # rename the user input file
        # new_user_input_file_name = uname_dir + '_' + user_input_file_name
        # new_user_input_source = user_input_target
        # new_user_input_target = user_upload_dir + '/' + new_user_input_file_name
        # shutil.move(new_user_input_source, new_user_input_target)
        #
        # # upload user input to yact server dif path
        # yact_session.sendline("cd " + yact_server_dif_path)
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # yact_scp_cmd = "scp -r " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + new_user_input_target + " ./"
        # yact_session.sendline(yact_scp_cmd)
        # yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=50)
        # if yact_ret == 0:
        #     raise Exception("\nscp to webserver timeout \n")
        # elif yact_ret == 1:
        #     yact_session.sendline(WEB_SERVER_PASSWORD)
        # elif yact_ret == 2:
        #     logging.info('\n%s \n' % yact_session.before)
        #     yact_session.sendline("yes")
        #     yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=50)
        #     if yact_ret == 0:
        #         raise Exception("\nscp to webserver timeout \n")
        #     elif yact_ret == 1:
        #         logging.info('\n%s \n' % yact_session.before)
        #         yact_session.sendline(WEB_SERVER_PASSWORD)
        #
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # user_found.progressBarData = "82"
        # user_found.save()
        #
        # # generate output by DIF tool
        # # python dif_fill.py -i input-dif.xlsm -u user-input-xuxiao.xlsx -o output-xuxiao.xlsm
        # # cp output-xuxiao.xlsm  /home/darcy/YACT/
        #
        # yact_output_name = "output_" + new_user_input_file_name.strip("xlsx") + "xlsm"
        # yact_gen_output_cmd = "python dif_fill.py -i input-dif.xlsm -u " + \
        #                       new_user_input_file_name + " -o " + yact_output_name
        #
        # logging.info('\n%s \n' % yact_gen_output_cmd)
        #
        # yact_session.sendline(yact_gen_output_cmd)
        # yact_session.expect(yact_prompt, timeout=300)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # yact_session.sendline("mv " + yact_output_name + " " + yact_server_yact_path)
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # # remove uploaded user input file
        # yact_session.sendline("rm -rf " + new_user_input_file_name)
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # user_found.progressBarData = "84"
        # user_found.save()
        #
        # # generate ne_xxx  YAML & SCRIPTS
        # yact_session.sendline("cd " + yact_server_yact_path)
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # # ./yact.sh gen-by-dif output-xuxiao.xlsm 7510-CE C710.ad1115
        # yact_yaml_cmd = "./yact.sh " + "gen-by-dif " + yact_output_name + " 7510-CE C710.ad1115"
        # yact_session.sendline(yact_yaml_cmd)
        # yact_session.expect(yact_prompt, timeout=100)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # # delete output xlsm file
        # yact_session.sendline("rm -rf " + yact_output_name)
        # yact_session.expect(yact_prompt)
        # logging.info('\n%s \n' % yact_session.before)
        #
        # # download ne_xxx to user_upload_dir
        # yact_scp_cmd = "scp -r " + "./ne-xxx/ " + WEB_SERVER_USERNAME + "@" + WEB_SERVER_IP + ":" + user_upload_dir
        # yact_session.sendline(yact_scp_cmd)
        # yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword:', 'connecting (yes/no)?'], timeout=5)
        # if yact_ret == 0:
        #     raise Exception("\nscp to webserver timeout \n")
        # elif yact_ret == 1:
        #     yact_session.sendline(WEB_SERVER_PASSWORD)
        # elif yact_ret == 2:
        #     logging.info('\n%s \n' % yact_session.before)
        #     yact_session.sendline("yes")
        #     yact_ret = yact_session.expect([pexpect.TIMEOUT, '[p|P]assword'], timeout=5)
        #     if yact_ret == 0:
        #         raise Exception("\nscp to webserver timeout \n")
        #     elif yact_ret == 1:
        #         logging.info('\n%s \n' % yact_session.before)
        #         yact_session.sendline(WEB_SERVER_PASSWORD)
        #
        # yact_session.expect(yact_prompt, timeout=200)
        # logging.info('\n%s \n' % yact_session.before)

    except Exception, e:
        logging.error('\nproblem during ssh to yact server: %s \n' % str(e))
        return False











