# mgw7510-web
This project is used to offer a web tool for easy utilities for both developer and tester in Nokia SBC department. 

The function of the web tool including but not limited to:

1. SBC deployment for version: HE; CE; iSBC-RMS; iSBC-CLOUD VMware; iSCB-CLOUD Openstack
2. Knowledge search
3. DIF TOOL


###################   RELEASE INFORMATION ######################
DEMO 1.0
User Administration function is finished, including:
   1. user registered
   2. change password
   3. forget password
   4. session and cookies based on user

Updated at 2017.1.5
Three bugs need to be fixed in future:
1. After click log out, then click backup button in the browser, 
   and finally a login-in page is displayed which is not expected.

   so, refresh the page is needed when click backup button on bowser.
   Same problem occurred on ce_deploy start/stop.

2. The log file "text/plain"  will be downloaded instead of displayed 
   on the browser. ( step1. use chrome, click start. 
                     step2. click refresh
                     step3. click stop
                     step4. click log

3. No content will be displayed on the log




####################   ROAD MAP  ##############################
1. Auto deployment for CE is under developing by Xu Xiao.
2. Auto deployment for HE is under developing by Zhao Peng.
3. DIF tool improvement is under developing by Ling Yan.

#################### JOIN US ##############################
If you want to join in our project, please contact me: 
      Xiao.A.Xu@alcatel-sbell.com.cn
Folk the repo and pull it after develop. So easy, right?


