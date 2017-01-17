#!/bin/bash

# This script is ued to check whether webserver could 
# connect to specific host 

##############################################################
# code is removed
# PING=`ping -c 3 $1 | grep '0 received' | wc -l`
# result=true
# for arg in $@
# do
#    echo -e
#    ping -c 1 $arg
#    if [ $? != 0 ]
#    then 
#       echo "PING $arg failed, please check"
#       result=false
#       break
#    fi
# done
#echo $result
############################################################

#sub function in the script
pingHost(){
    local result=2
    ping -c 1 $1
    if [ $? != 0 ]
    then
       # PING failed, please check
       result=0
    fi
    return $result
}

# main function
# $1 is the log file
# $2 is the IP address
# pingHost $2 >> $1
pingHost $1








