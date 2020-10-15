#The code to connect to switches via ip from ip.txt and creates a vlan 2000 RSPAN and adds it to all ports in trunk mode, 
#and also creates a rspan session 1 for vlan from the vlan.txt file.
#After making the settings, output for verification:
#    sh mon sess all
#    sh int tru | be Vlans in spanning tree forwarding state and not pruned
#    sh vtp status | inc VTP Operating Mode
#and is written to a txt file 'verify' + current date & time
import time
import copy
import paramiko
import re
import datetime
import sys

def connect_switch(swip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        output = ''
        getshrun = []
        swip_in_file = 0
        vlan_in_file = 0
        try:
            client.connect(swip, username=USER, password=PASSWORD)
            chan = client.invoke_shell()
            chan.send('term len 0\n')
            time.sleep(1)
            chan.send('term width 500\n')
            time.sleep(1)
            output = chan.recv(99999)
            chan.send('sh vl br\n')
            time.sleep(1)
            print('!')
            print('==============',swip,'==============')
            output = (chan.recv(99999)).decode('utf8')
            output = output.split('\r\n')
            for line in output:
                    if re.search('^\d{3}\s', line) != None:
                            with open('vlan.txt', 'r') as vlan_list:
                                    for vlan in vlan_list:
                                            if int((re.search('^\d{3}\s', line).group()).strip(' ')) == int(vlan):
                                                    chan.send('conf t\n \
                                                            vtp mode transparent \n \
                                                            spanning-tree extend system-id \n \
                                                            vlan 2000\n \
                                                             name Vl_2000_RSAPN\n \
                                                             remote-span\n \
                                                             exit\n \
                                                            monitor session 1 source vlan '+vlan+'\n \
                                                            monitor session 1 destination remote vlan 2000 \n \
                                                            exit\n ')
                                                    time.sleep(1)
                                                    chan.send('sh int tru | inc trunkin\n')
                                                    time.sleep(1)
                                                    output = (chan.recv(99999)).decode('utf8').split('\r\n')
                                                    for line_trunk in output:
                                                            if re.search('trunking', line_trunk) != None:
                                                                    if re.search('^\w\w\d(/\d+)+', line_trunk) != None:
                                                                            port_trunk = re.search('^\w\w\d(/\d+)+', line_trunk).group()
                                                                            chan.send('conf t\n \
                                                                                    int '+port_trunk+'\n \
                                                                                    switchport trunk allowed vlan add 2000\n \
                                                                                    end\n \
                                                                                    wr\n ')
                                                                            time.sleep(2)
                                                                            print(swip,',',vlan)
                                                                            if swip != swip_in_file and vlan != vlan_in_file:
                                                                                    with open(name_file, 'a') as f_result:
                                                                                            swip_in_file = swip
                                                                                            vlan_in_file = vlan
                                                                                            w = (swip,',',vlan)
                                                                                            f_result.writelines(w)
                                                                    else:
                                                                          print(line_trunk)  
            client.close()
        except Exception as e:
            print(e, '!!!!!!!!!!!!!!!---CONNECTION ERROR---!!!!!!!!!!!!!!!')

def verify_switch(swip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        output = ''
        getshrun = []
        try:
            client.connect(swip, username=USER, password=PASSWORD)
            chan = client.invoke_shell()
            chan.send('term len 0\n')
            time.sleep(1)
            chan.send('term width 500\n')
            time.sleep(1)
            output = chan.recv(99999)
            chan.send('sh mon sess all\n \
                        sh int tru | be Vlans in spanning tree forwarding state and not pruned\n \
                        sh vtp status | inc VTP Operating Mode \n')
            time.sleep(1)
            output = (chan.recv(99999)).decode('utf8')
            print('!')
            print('============================',swip,'============================')
            print(output)            
            with open(name_file_verify, 'a') as f_result:
                    w = ('============================',swip,'============================')
                    f_result.writelines(w)
                    f_result.writelines(output)
                    f_result.writelines('\n')
            client.close()
        except Exception as e:
            print(e, '!!!!!!!!!!!!!!!---CONNECTION ERROR---!!!!!!!!!!!!!!!')

        #Create a txt file 'ip_verify' + current date & time for saving ip switch & vlan
name_file = ('ip_verify'+datetime.datetime.now().strftime("%Y%m%d_%H-%M")+'.txt')

USER = 'USER_LOGIN'
PASSWORD = 'USER_PASSWORD'
with open('ip.txt', 'r') as ip_list:
        for swip in ip_list:
                connect_switch(swip.strip())

        #Waining for working spanning-tree & vlan 2000 will be active at trunk ports
time.sleep(60)

        #Create a txt file 'verify' + current date & time for saving verification
name_file_verify = ('verify'+datetime.datetime.now().strftime("%Y%m%d_%H-%M")+'.txt')

with open(name_file, 'r') as ip_list:
        for swip in ip_list:
                swip = re.search('^((\d)+\.)+(\d)+', swip)                
                if swip != None:
                        verify_switch(swip.group().strip())