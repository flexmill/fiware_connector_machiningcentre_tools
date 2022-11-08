##
#run this script local

import re, time
import goodpartscounter as gpc
import ideal_cycle_time as ict
import paramiko
from scp import SCPClient
import time
import datetime
import subprocess

#machining centre access data 
host = 'xxx' #Machining centre adress
port = 'xx' # Port of machining centre
username = 'xxx' #Username of machining centre
password = 'xxx' #Password of machining centre

#paths
local_path = r'xxx' #local path where simulation data shall be saved to 
ori_local_path = r'xxx' #local path where original data shall be saved to 
rem_path = 'xxx' # path machining centre
filename = "xxx" #filename of machining data
local_path_tool_life = 'xxx' #local path where tool life data shall be saved to 
filename_tool_life = 'xxx' #file name where tool life data shall be saved to 

# database good parts counter and ideal cycle time of ERP System
server = 'xxx'
database = 'xxx'
username_sql = 'xxx'
password_sql = 'xxx'


is_active = True


def createSSHClient(host, port, username, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password, banner_timeout=50, auth_timeout=30)
    return client


# compare new line with last line
def Compare(machine):
    # print(machine)

    # read lastline from machine E file
    with open(ori_local_path + "\\" + filename + "_" + machine + ".SPF", 'r') as ori_file:
        # timestamp machine
        output = list(ori_file).pop().split()

    # read lastline from machine A file
    with open(ori_local_path + "\\" + filename + "_" + machine + "_A.SPF", 'r') as ori_file:
        # timestamp machine
        try:
            output_A = list(ori_file).pop().split()
        except:
            print("list was empty??")

    # read lastline from IRKFISH.TXT
    with open(local_path + "\\" + filename + "_" + machine + ".TXT", 'r') as file:
        # timestamp last part
        lastline = list(file).pop(-2).split()

    # read lastline from IRKFISH.TXT
    with open(local_path + "\\" + filename + "_" + machine + ".TXT", 'r') as file:
        # timestamp last part
        lastline_A = list(file).pop().split()

    # read all lines from IRKFISH.TXT
    with open(local_path + "\\" + filename + "_" + machine + ".TXT", 'r') as file:
        irkfish_all_lines = file.read().splitlines()

    ## Prepare data from time stamp files in order to be able to write to IRKFISH.TXT for Anfang time A
    textline = output_A

    digits = re.findall('\d+', str(output_A))

    if len(digits[0]) != 6:
        del digits[0]

    good_parts_counter = gpc.getCounter(machine, server, database, username_sql, password_sql, textline[3])

    ideal_cycle_time = ict.get_ideal_cycle_time(machine, server, database, username_sql, password_sql, digits[0])

    if str(good_parts_counter) == "None":
        good_parts_counter = lastline[4]

    new_line_A = digits[0] + '\t' + textline[1] + '\t' + textline[2] + '\t' + textline[3] + '\t' + str(
        good_parts_counter) + '\t' + textline[4] + '\t' + str(ideal_cycle_time) + '\n'
    new_line_A_list = [digits[0], textline[1], textline[2], textline[3], str(good_parts_counter), textline[4],
                       str(ideal_cycle_time)]

    ## Prepare data from time stamp files in order to be able to write to IRKFISH.TXT for End time E
    textline = output

    digits = re.findall('\d+', str(output))

    if len(digits[0]) != 6:
        del digits[0]

    new_line_E = digits[0] + '\t' + textline[1] + '\t' + textline[2] + '\t' + textline[3] + '\t' + str(
        good_parts_counter) + '\t' + textline[4] + '\t' + str(ideal_cycle_time) + '\n'
    new_line_E_list = [digits[0], textline[1], textline[2], textline[3], str(good_parts_counter), textline[4],
                       str(ideal_cycle_time)]

    datetime_timestamp_A = datetime.datetime.strptime(new_line_A_list[1] + new_line_A_list[2], '%d.%m.%Y%H:%M:%S')
    datetime_timestamp_E = datetime.datetime.strptime(new_line_E_list[1] + new_line_E_list[2], '%d.%m.%Y%H:%M:%S')

    # Compare datetimes to order the last and before last time stamps to write it in the right order
    if datetime_timestamp_A < datetime_timestamp_E:
        new_line_1 = new_line_A[:-1]  # Without last new line character to be able to search on IRKFISH.TXT
        new_line_1_list = new_line_A_list
        new_line_2 = new_line_E[:-1]  # Without last new line character to be able to search on IRKFISH.TXT
        new_line_2_list = new_line_E_list
    elif datetime_timestamp_E < datetime_timestamp_A:
        new_line_1 = new_line_E[:-1]  # Without last new line character to be able to search on IRKFISH.TXT
        new_line_1_list = new_line_E_list
        new_line_2 = new_line_A[:-1]  # Without last new line character to be able to search on IRKFISH.TXT
        new_line_2_list = new_line_A_list
    else:  # of both times are identical
        new_line_1 = new_line_A[:-1]  # Without last new line character to be able to search on IRKFISH.TXT
        new_line_1_list = new_line_A_list
        new_line_2 = new_line_E[:-1]  # Without last new line character to be able to search on IRKFISH.TXT
        new_line_2_list = new_line_E_list

    ##Check if new_line_A and _E are already in the IRKFISH.TXT and if not then write the new line
    if new_line_1 not in irkfish_all_lines:
        with open(local_path + "\\" + filename + "_" + machine + ".TXT", 'a') as newfile:
            newfile.write(new_line_1 + '\n')
    if new_line_2 not in irkfish_all_lines:
        with open(local_path + "\\" + filename + "_" + machine + ".TXT", 'a') as newfile:
            newfile.write(new_line_2 + '\n')


while is_active:

    for host in hosts:

        try:
            machine = host.split(".")
            del machine[0]
            del machine[2]

            machine = machine[0] + machine[1]

            cmds = f"C:\Program Files\PuTTY\plink {username}@{host} -pw {password} cd {rem_path}\n head {filename}.SPF\n exit\n"
            # Siemens 840D SL Read file from machine
            output_E = subprocess.check_output(cmds, stdin=subprocess.PIPE).decode('utf-8')
            cmds = f"C:\Program Files\PuTTY\plink {username}@{host} -pw {password} cd {rem_path}\n head {filename}_A.SPF\n exit\n"

            # Siemens 840D SL Read file from machine
            output_A = subprocess.check_output(cmds, stdin=subprocess.PIPE).decode('utf-8')

            with open(ori_local_path + "\\" + filename + "_" + machine + ".SPF", 'w') as ori_file:
                ori_file.write(output_E.strip())

            with open(ori_local_path + "\\" + filename + "_" + machine + "_A.SPF", 'w') as ori_file:
                ori_file.write(output_A.strip())


            time.sleep(20)

            Compare(machine)

        except:
            pass


        try:
            cmds = f"C:\Program Files\PuTTY\plink {username}@10.10.65.1 -pw {password} cd {rem_path}\n head {filename_tool_life}.SPF\n exit\n"
            # Siemens 840D SL Read file from machine
            output_tool_life = subprocess.check_output(cmds, stdin=subprocess.PIPE).decode('utf-8')

            with open(local_path_tool_life + "\\" + filename_tool_life + "_" + output_tool_life.split("_")[0] + ".csv",
                      'w') as ori_file:
                ori_file.write(output_tool_life.replace('\t', ';'))
        except:
            pass
