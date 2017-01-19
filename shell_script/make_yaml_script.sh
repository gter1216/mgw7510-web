#!/bin/bash

#######################################################
################ Author: Xu Xiao ######################
################ Date: 2017.01.18 #####################
#######################################################

# arguments:
# $1 ==> uname_dir

# uname_dir ==> Xiao.A.Xu_alcatel-sbell.com.cn
uname_dir=$1


################# Global Var    #######################
user_upload_dir="../UserWorkDir/$uname_dir/ce_deploy_dir/UserUploadDir"
yact_tool_dir="../YACT"
yact_work_dir="../YACT/UserDir/$uname_dir"


################# main function #######################

################# step1: move files to yact work dir

# create yact work dir if not exist
# if exists, clean all the files
if test ! -d $yact_work_dir
then
   mkdir $yact_work_dir
else
   cd $yact_work_dir && rm -rf *
fi






# change to UserUploadDir and clean old YACT files
#cd ../UserWorkDir/$uname_dir/ce_deploy_dir/UserUploadDir && rm -rf YACT/
# unzip csar and yact
#find ./ -name '*.zip' -exec unzip -o {} \;
# copy common tools to UserUploadDir
#cp -r ../../../../YACT/ ./
# set env
#cd YACT
#yang_root_dir=\'`pwd`/YANG_ROOT\'
#yang_root="YANG_ROOT="$yang_root_dir
#yang_gurl="YANG_GURL="$yang_root_dir
#echo $yang_root > setup.env && echo $yang_gurl >> setup.env
# restart yact, this is tricky, do not need sleep 2s,
# var= could wait the shell script return
#stop_result=`./yact.sh svc stop`
#start_result=`./yact.sh svc start`
# get version
#version=`./yact.sh list version 7510-CE`
#echo "list version result is: "$version

















