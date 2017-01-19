#!/bin/bash

#######################################################
################ Author: Xu Xiao ######################
################ Date: 2017.01.18 #####################
#######################################################

# arguments:
# $1 ==> uname_dir

# return results:
# 3 ====> did not find supported yact version, please use
#         ./yact.sh list version 7510-CE to check


# uname_dir ==> Xiao.A.Xu_alcatel-sbell.com.cn
uname_dir=$1

################# Global Var    #######################
# shell_dir = /home/projects/mgw7510_webserver/R01/shell_script
shell_dir=`pwd`
# home_dir = /home/projects/mgw7510_webserver/R01/
home_dir=$(dirname "$PWD")
user_upload_dir="${home_dir}/UserWorkDir/${uname_dir}/ce_deploy_dir/UserUploadDir"
yact_tool_dir="${home_dir}/YACT"
yact_work_dir="${home_dir}/YACT/UserDir/${uname_dir}"

#cd "$user_upload_dir/nokia.vMGW_C71_M_O_3.0.01.default.csar/bulk-config"

cd "${yact_work_dir}/ne-xxx/bulk/"
echo `pwd`
ls

cd $user_upload_dir
cd *.csar
echo `pwd`
cp -r ${yact_work_dir}/ne-xxx/bulk/* ./bulk-config/





