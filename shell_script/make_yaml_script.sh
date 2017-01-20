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

# usage:
# ./make_yaml_script.sh Xiao.A.Xu_alcatel-sbell.com.cn

################# Global Var    #######################
# shell_dir = /home/projects/mgw7510_webserver/R01/shell_script
shell_dir="$( cd "$( dirname "$0"  )" && pwd  )"
echo "shell script dir is: "${shell_dir}
# home_dir = /home/projects/mgw7510_webserver/R01/
home_dir=$( dirname "${shell_dir}" )
echo "home dir is: "${home_dir}
user_upload_dir="${home_dir}/UserWorkDir/${uname_dir}/ce_deploy_dir/UserUploadDir"
yact_tool_dir="${home_dir}/YACT"
yact_work_dir="${home_dir}/YACT/UserDir/${uname_dir}"

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

cp ${user_upload_dir}/yact*.zip ${user_upload_dir}/*.xlsx $yact_work_dir

# get version
cd $yact_work_dir
# yact-C710.B00.ae1b1716.zip or
# yact-nokia-SBC_media-C710.B00.ae110417.zip
yact_name=`ls yact*.zip`
# B00.ae1b1716.zip
yact_name=${yact_name#*C710.}
# B00.ae1b1716
yact_name=${yact_name%.zip*}
# C710.B00.ae1b1716
version=C710.$yact_name
echo "version is: "$version

# DIF FILL TOOL PATH
dif_fill_tool_path="${yact_work_dir}/DIF_TOOLS/DIF_FILL/7510-CE/$version"

# unzip yact*.zip
cd $yact_work_dir && unzip yact*.zip && rm -rf yact*.zip
mv *.xlsx $dif_fill_tool_path


################# step2: generate output dif file
cd $dif_fill_tool_path
python dif_fill.py -i input-dif.xlsm -u *.xlsx -o output.xlsm


################# step3: check current version 
cd $yact_tool_dir
# C710.B00.ae1a3116
supported_version=`./yact.sh list version 7510-CE`
echo "current supported version is: "$supported_version
compare_result=`echo $supported_version | grep $version`
if [ "$compare_result" = "" ] 
then 
   # did not find supported version
   echo "did not find supported version"
   # cover yact common tool YANG_ROOT dir
   cp -r ${yact_work_dir}"/YACT/YANG_ROOT" $yact_tool_dir
   echo "restart yact tool"
   ./yact.sh svc stop
   sleep 1s
   ./yact.sh svc start
   sleep 2s
   supported_version=`./yact.sh list version 7510-CE`
   echo "current supported version is: "$supported_version
   compare_result=`echo $supported_version | grep $version`
   if [ "$compare_result" = "" ]
   then
      exit 3
   else
      echo "found supported version"
   fi
else
   echo "found supported version" 
fi

################# step4: make yaml and scripts
cd $yact_tool_dir
./yact.sh gen-by-dif ${dif_fill_tool_path}"/output.xlsm" "7510-CE" $version $yact_work_dir

################# step5: replace user_upload_dir csar
cd $user_upload_dir && unzip -o *.csar.zip && rm -rf *.csar.zip

cd ${yact_work_dir}"/ne-xxx/bulk/" && cp * ${user_upload_dir}/*.csar/bulk-config
cd ${yact_work_dir}"/ne-xxx/deployment/" && cp *.yaml ${user_upload_dir}/*.csar/scripts/cloud_config/


#cp -r ${yact_work_dir}"/ne-xxx/bulk/*" ./bulk-config/
#cp -r ${yact_work_dir}"/ne-xxx/deployment/*.yaml" ./scripts/cloud_config/

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

