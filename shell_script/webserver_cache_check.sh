#!/bin/bash

###########################################################
################### Author: xu xiao   #####################
################### Date:   2017.01.12 ####################
###########################################################

# This script is used to check cache on webserver 

# arguments:
# $1 ===> ce_deploy_dir
# $2 ===> qcow2_name
# $3 ===> qcow2_md5
# $4 ===> disk_limit
# ./webserver_cache_check.sh /home/projects/mgw7510_webserver/R01/cache_dir/ce_deploy nokia.qcow2 234eds 100

# return result: 
# 1 ====> no cache qcow2 find or md5 validate failed;
# 2 ====> error occurred, no enough disk storage;
# 3 ====> cached qcow2 find and md5 validate passed

ce_deploy_dir=$1
qcow2_name=$2
qcow2_md5=$3
disk_limit=$4

# sub function

clean_outdated_qcow2(){
     # clean the oldest qcow2 in cache file
     oldest_file=`ls -rt | head -1`
     rm -rf $oldest_file
     
     left_disk=` df -h /home | grep "/dev/mapper" | awk '{print int($4)}' ` 
	 
     if [ $left_disk -le $disk_limit ]
     then
         # after clean work, there is still no enough disk
	 exit 2
     else
	 # after clean work, there is enough disk
	 exit 1
     fi	 
}


# main function
cd $ce_deploy_dir
left_disk=` df -h /home | grep "/dev/mapper" | awk '{print int($4)}' `

# if left disk storage smaller than 4G, then report error.
if [ $left_disk -lt 10 ]
then
    # no enough disk
    exit 2
fi

cd qcow2_cache_dir

if test -e $qcow2_name
then
    # qcow2 exist, then caculate md5 value
    md5value=`md5sum $qcow2_name | cut -d ' ' -f1`
    if [ $md5value = $qcow2_md5 ]
    then
        exit 3
    else
        exit 1
    fi
else
    # qcow2 not exist, check if there is enough disk to upload new qcow2 file to buffer dir
    if [ $left_disk -le $disk_limit ]
    then
    	# if left disk storage smaller than $disk_limit
    	cd qcow2_cache_dir
        clean_outdated_qcow2
    else
        # no cached qcow2 find, and there is enough disk
        exit 1
    fi
fi
