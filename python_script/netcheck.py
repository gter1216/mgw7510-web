import commands
import logging
import ce_deploy_scripts


def get_host_conn_state(hosts):

    for key in hosts:
        logging.info('\ncheck connection with %s\n' % key)
        shell_file_path = ce_deploy_scripts.BASE_DIR + "/shell_script/netping.sh"
        shell_cmd = "sh " + shell_file_path + " " + hosts[key]
        output = commands.getstatusoutput(shell_cmd)
        logging.info('\n%s\n' % output[1])
        if output[0] == 0:
            logging.error('\nhost %s is unavailable\n' % key)
            return False

    return True
