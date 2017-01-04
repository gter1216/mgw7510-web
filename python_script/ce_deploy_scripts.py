from mgw7510.models import WebUser
from pexpect import pxssh
import re

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

    print uname
    print select_rel
    print select_pak

    user_found = WebUser.objects.get(username=uname)

    work_dir = user_found.userWorkDir + "/ce_deploy_dir/"


















