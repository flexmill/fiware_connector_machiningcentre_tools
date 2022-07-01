##
#run this script local

import re, time
import goodpartscounter as gpc
import paramiko
from scp import SCPClient

#machine data
host = 'xxx' #Machining centre adress
port = 'xx' # Port of machining centre
username = 'xxx' #Username of machining centre
password = 'xxx' #Password of machining centre

#paths
local_path = r'xxx' #local path where simulation data shall be saved to 
ori_local_path = r'xxx' #local path where original data shall be saved to 
rem_path = 'xxx' # path machining centre
filename = "xxx" #filename of machining data


is_active = True

def createSSHClient(host, port, username, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password, banner_timeout=10)
    return client

# compare new line with last line
def Compare():
    # read lastline from machine file
    with open(ori_local_path + "\\" + filename + ".SPF", 'r') as ori_file:
        # timestamp machine
        output = list(ori_file).pop().split()


    #read lastline from IRKFISH.TXT
    with open(local_path + "\\" + filename + ".TXT", 'r') as file:
        # timestamp last part
        lastline = list(file).pop().split()


    time.sleep(2)

    if output[2] != lastline[2]:
        machine = host.split(".")
        del machine[0]
        del machine[2]

        machine = machine[0] + machine[1]

        good_parts_counter = gpc.getCounter(machine, server, database, username_sql, password_sql)

        textline = output
        digits = re.findall('\d+', str(output))

        if len(digits[0]) != 6:
            del digits[0]

        new_line = digits[0] + '\t' + textline[1] + '\t' + textline[2] + '\t' + textline[3] + '\t' + str(good_parts_counter) + '\n'

        with open(local_path + "\\" + filename + ".TXT", 'a') as newfile:
            newfile.write(new_line)

while is_active:

    ssh = createSSHClient(host, port, username, password)
    scp = SCPClient(ssh.get_transport())
    scp.get(rem_path + "/" + filename + ".SPF", ori_local_path)

    Compare()



