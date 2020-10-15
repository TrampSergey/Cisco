#The code to connect to switches via ip from ip.txt and creates a vlan 2000 RSPAN and adds it to all ports in trunk mode, 
#and also creates a rspan session 1 for vlan from the vlan.txt file.
#After making the settings, output for verification:
#    sh mon sess all
#    sh int tru | be Vlans in spanning tree forwarding state and not pruned
#    sh vtp status | inc VTP Operating Mode
#and is written to a txt file 'verify' + current date & time
