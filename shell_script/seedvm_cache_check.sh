#!/bin/bash

###########################################################
################### Author: xu xiao   #####################
################### Date:   2017.01.12 ####################
###########################################################

# This script is used to build cache for qcow2 on seedvm
# if there is no cache. If there is cached qcow2 and md5
# verification passed, then create image on openstack
# and then return result to python main calling process.

# arguments:
# $1 ===> /root/auto_ce_deploy
# $2 ===> qcow2_name
# $3 ===> qcow2_md5
# $4 ===> disk_limit
# $5 ===> source_file
# $6 ===> uname
# $7 ===> sw_image_name

# return result:
# 1 ====> no cache qcow2 find;
# 2 ====> error occurred, no enough disk storage;
# 3 ====> cached qcow2 find and create image failed
# 4 ====> cached qcow2 find and create image success

work_dir=$1
qcow2_name=$2
qcow2_md5=$3
disk_limit=$4
source_file=$5
uname=$6
sw_image_name=$7

buffer_dir="buffer_dir"
cache_dir="cache_dir"

# sub function

# create work dir and sub dir
create_dir(){
     if test ! -d $1
     then
     # main dir not exists, create it
         mkdir $1
         cd $1
         mkdir $buffer_dir
         mkdir $cache_dir
         exit 1
     else
          cd $1
          if test ! -d $buffer_dir
          then
      	      # buffer_dir is not exist, create it
      	      mkdir $buffer_dir
          fi

          if test ! -d $cache_dir
          then
      	      # cache_dir is not exist, create it
      	      mkdir $cache_dir
              exit 1
          fi
     fi
}

# create image file
create_image(){
      #source $2
      . $2
      uname_local=$3
      #pure_qcow2_name=${qcow2_name_local%.*}"_auto_"${uname_local}
      sw_image_name=$1
      echo "glance image-create --name=$4 --file=$1 --disk-format=qcow2 \
            --container-format=bare --is-public=false --is-protected=false"
      glance image-create --name=$4 --file=$1 --disk-format=qcow2 \
                          --container-format=bare --is-public=false --is-protected=false
}

clean_outdated_qcow2(){
      ###################################
      # The code is commented
      if false
      then
          # clean the qcow2 which is outdate of 1 days
          # find ./ -mmin 180 -print | xargs rm -rf
          # find $1 -mtime +1 -type f | xargs rm -f

          # first find oldest file, then caculate how old it is
          # if it older than 1 hours, then remove it
          oldest_file=`ls -rt | head -1`
          modify_time=`stat -c %Y $oldest_file`
          now_time=`date +%s`
          time_diff=$(($now_time-$modify_time))

          if  [ $time_diff -gt 3600 ]
          then
              rm -rf $oldest_file
          fi
      fi
      #####################################

      # clean the oldest qcow2 in cache file
      cd $1
      oldest_file=`ls -rt | head -1`
      rm -rf $oldest_file

      left_disk=` df -h /root | grep "/dev/vda1" | awk '{print int($4)}'`

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
cd /root
left_disk=` df -h /root | grep "/dev/vda1" | awk '{print int($4)}'`

# if left disk storage smaller than 4G, then report error.
if [ $left_disk -lt 4 ]
then
    # no enough disk
    exit 2
fi

create_dir $work_dir

cd $work_dir

cd $cache_dir

if test -e $qcow2_name
then
    # qcow2 exist, then caculate md5 value
    md5value=`md5sum $qcow2_name | cut -d ' ' -f1`
    if [ $md5value = $qcow2_md5 ]
    then
        echo $md5value
    	create_image $qcow2_name $source_file $uname $sw_image_name
        # md5 validate passed
        # create image file on openstack

        if [ $? != 0 ]
        then
       	   # create image failed
       	   exit 3
       	else
       	   # create image success
       	   exit 4
       	fi
    fi
else
    # qcow2 not exist, check if there is enough disk to upload new qcow2 file to buffer dir
    if [ $left_disk -le $disk_limit ]
    then
    	  # if left disk storage smaller than $disk_limit
          cd $work_dir
    	  clean_outdated_qcow2 $cache_dir
    else
        # no cached qcow2 find, and there is enough disk
        exit 1
    fi
fi
