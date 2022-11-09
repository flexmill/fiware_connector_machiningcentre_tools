##
# run this script on remote pc within company network to access machining data and transfer to FIWARE Context Broker
#
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
import callrest as cr
import orioncb as ocb
import json #For general json file export
import pathlib
import csv
import WorkOrder_ToolList as wo

local_path = 'xxx' #Path to file of machining centre runtimes that were exported by IRKSFISH_A.SPF, IRKSFISH_E.SPF and irkfish_copy.py
local_path_tool = 'xxx' #Path to file of machining centre tool lifes that were exported by TOOL_LIFE.SPF and irkfish_copy.py
sim_path = 'xxx' #Path to simulated runtimes for definition of ideal cycle times
machines = ['xxx', 'xxx,'] #List of machining centres that shall be observed 

ocb_hostname = os.getenv("ORION_HOST", "orion") #set hostname in docker-compose file
ocb_port = os.getenv("ORION_HOST", "1026") #set port in docker-compose file
urlOrion = "http://{}:{}".format(ocb_hostname,ocb_port)

path_wo = 'xxx' #Path to work order file that shall be read
machines_wo = {'xxx': 'xxx'} #Dictionary of machines for which work orders shall be performed
server = 'xxx' #Server where Wintool is running
database = 'xxx' #Database of tool in Wintool
name_toollist = 'xxx' #Name of specific tool List

class _CustomHandler(FileSystemEventHandler):
    def on_modified(self, event):
        machine = str(event.src_path)[-8:-4]
        for i in machines: 
            if machine in i:
                filename="\\IRKFISH_"+machine
        writeFIWARE(filename, machine)

class _CustomHandlerTool(FileSystemEventHandler):
    def on_modified(self, event):
        machine = str(event.src_path)[-8:-4]
        for i in machines: 
            if machine in i:
                filename="\\TOOL_LIFE_"+machine
        writeToolLife(filename, local_path_tool)
        #Call Work Order and write work order and compare create delta tool lists from Wintool:
        wo.work_order(urlOrion, path_wo, machines_wo, server, database, name_toollist)


def CalcCycleTime(lastline, penultimateline1, penultimateline2):
    
    # Try to check the third last lines:
    penultimateline = penultimateline2
    lastline = penultimateline1
    
    if lastline[0] == penultimateline[0]: #Check if it is not a new article
        
        #Normal machining with start and end time
        if lastline[5] == 'E' and penultimateline[5] == 'A':
            lastline_new = lastline
            penultimateline_new = penultimateline
            
        #penultimate is E and lastline is A meaning that these two time stamps are between downtime and the start of the next part, hence it shall not be counted for up time 
        elif lastline[5] == 'A' and penultimateline[5] == 'E':
            lastline_new = lastline
            penultimateline_new = lastline 
            
        #More than two times  program restarted and hence no E meaning that program was stopped and part was scraped
        elif lastline[5] == 'A' and penultimateline[5] == 'A':
            lastline_new = lastline
            penultimateline_new = lastline #If two As then write same time to timestamp meaning that this time is not written into FIWARE because its downtime
        
        #No A value and hence meaning that some problem ocurred and shall be counted for down time
        elif lastline[5] == 'E' and penultimateline[5] == 'E':
            lastline_new = lastline
            penultimateline_new = lastline #If two As then write same time to timestamp meaning that this time is not written into FIWARE because its downtime
        
        else:
            lastline_new = lastline
            penultimateline_new = lastline
    
    else: #If article are different then no new entry shall be written to FIWARE
        lastline_new = penultimateline
        penultimateline_new = penultimateline
    
    return penultimateline_new, lastline_new



def writeFIWARE(filename, machine):

    with open(local_path + filename + ".TXT", 'r') as file:
        # timestamp last part
        a=list(file)
        lastline = a.pop().split()
        penultimateline1 = a.pop().split()
        penultimateline2 = a.pop().split()
        
    penultimateline_new, lastline_new = CalcCycleTime(lastline, penultimateline1, penultimateline2)

    try:
        with open(sim_path + "\RUNTIME_SIM.SPF", 'r') as sim_file:
            #timestamp SIM Part
            sim_line = list(sim_file).pop().split()
        ideal_cycle_time = sim_line[4]
 
    except: #If no simulated ideal cycle time is available then take ideal cycle time from ERP system 
        ideal_cycle_time = 0.9*float(penultimateline_new[6])
    
    
    timestamp_start = {"article_number": penultimateline_new[0], "date": penultimateline_new[1], "time": penultimateline_new[2], "charge": penultimateline_new[3], "ideal_cycle_time": ideal_cycle_time, "good_parts_counter": penultimateline_new[4]}
    timestamp_end = {"article_number": lastline_new[0], "date": lastline_new[1], "time": lastline_new[2], "charge": lastline_new[3], "ideal_cycle_time": ideal_cycle_time, "good_parts_counter": lastline_new[4]}
        
    datetime_timestamp_start = datetime.datetime.strptime(timestamp_start["date"] + timestamp_start["time"], '%d.%m.%Y%H:%M:%S')
    datetime_timestamp_end = datetime.datetime.strptime(timestamp_end["date"] + timestamp_end["time"], '%d.%m.%Y%H:%M:%S')

    dt = datetime.date.today()
    
    print("dict creating")
    MachiningCentre = {
        "id": timestamp_start["article_number"],
        "type": "MachiningData",
        "Batch": {
            "type": "Text",
            "value": timestamp_start["charge"]},
        "MachiningCentre": {
            "type": "Int",
            "value": int(machine)},
        "IdealCycleTime": {
            "type": "Second",
            "value": ideal_cycle_time},
        "MachiningDateStart": {
            "type": "Date",
            "value": str(datetime_timestamp_start.date())},
        "MachiningTimeStart": {
            "type": "Time",
            "value": str(datetime_timestamp_start.time())},
        "MachiningDateEnd": {
            "type": "Date",
            "value": str(datetime_timestamp_end.date())},
        "MachiningTimeEnd": {
            "type": "Time",
            "value": str(datetime_timestamp_end.time())},
        "GoodPartsCount": {
            "type": "Int",
            "value": timestamp_start["good_parts_counter"]},
        "GoodPartsDateStart": {
            "type": "Date",
            "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))},
        "GoodPartsDateEnd": {
            "type": "Date",
            "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))}
    }

    part_update = {}
    part_update["Batch"] = {"type": "Text", "value": timestamp_start["charge"]}
    part_update["MachiningCentre"] = {"type": "Int", "value": int(machine)}
    part_update["IdealCycleTime"] = {"type": "Second", "value": ideal_cycle_time}
    part_update["MachiningDateStart"] = {"type": "Date", "value": str(datetime_timestamp_start.date())}
    part_update["MachiningTimeStart"] = {"type": "Time", "value": str(datetime_timestamp_start.time())}
    part_update["MachiningDateEnd"] = {"type": "Date", "value": str(datetime_timestamp_end.date())}
    part_update["MachiningTimeEnd"] = {"type": "Time", "value": str(datetime_timestamp_end.time())}
    part_update["GoodPartsCount"] = {"type": "Int", "value": timestamp_start["good_parts_counter"]}
    part_update["GoodPartsDateStart"] = {"type": "Date", "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))}
    part_update["GoodPartsDateEnd"] = {"type": "Date", "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))}

    if penultimateline1[0] != penultimateline2[0]:
        print("entity new")
        ocb.createEntities(urlOrion, MachiningCentre)
        ocb.deleteEntities(urlOrion, id=penultimateline2[0]) #Delete previous/old article number

    elif lastline_new != penultimateline_new:    #Check if a new real entry is written (new part made) and if yes write new entry into FIWARE
        #check if an entity exists or fi the context broker is empty:
        orion_output = ocb.readEntities(urlOrion, id=timestamp_start["article_number"]) #Output is a tuple with thte first an itneger with the error code as in integer 404
        if orion_output[0] == 404:
            print("entity new")
            ocb.createEntities(urlOrion, MachiningCentre)
        else:
            print("entity updated")
            ocb.updateEntities(urlOrion, part_update, timestamp_start["article_number"])
 
    else :
        print("nothing happens")
 
    path_current = pathlib.Path(__file__).parent.resolve()
    
    with open(os.path.join(path_current, "MachiningCentre.json"), "w") as outfile:
        json.dump(MachiningCentre, outfile)

        
        
def writeToolLife(filename, toolpath):
    
    with open(toolpath+filename+".CSV", 'r') as csvdatei:
        csv_reader_object =csv.reader(csvdatei, delimiter = ";")
        for row in csv_reader_object:
            index = row[0]
            machine = index[:4]
            articlenr = index[5:11]
       

    tool_life = {
        "id": articlenr+"_ToolLife",
        "type": "Tool_life"}
    
    tool_list= []    
    with open(toolpath + filename+".CSV", 'r') as csvdatei:
        csv_reader_object =csv.reader(csvdatei, delimiter = ";")
        for row in csv_reader_object:
            toolid = row [1]
            monitoring_type = row[2]
            target_quantity = row[3]
            limit = row[4]
            actual_quantity = row[5]
            
            tool_id_dic = {"id": toolid, toolid:{
            "monitoringtype" : {
               "type": "Int", 
               "value": monitoring_type},
            "targetquantity" : {
               "type": "Int", 
                "value": target_quantity},
            "warninglimit" : {
                "type": "Int",
                "value": limit},
            "actualquantity" : {
                "type": "Int",
                "value": actual_quantity}
                }}
            tool_list.append(tool_id_dic)
            
    
    toolupdate = {"type": machine, "value": tool_list} 
    tool_life[articlenr] = {"type": machine, "value": tool_list} 

    orion_output = ocb.readEntities(urlOrion, id=articlenr+"_ToolLife")
    
    if orion_output[0] == 404:
        ocb.createEntities(urlOrion, tool_life)
    else:
        if orion_output[1]["type"] == "Tool_life":
            ## First delete and then create new because update function does not work
            ocb.deleteEntities(urlOrion, id=articlenr+"_ToolLife")  
            ocb.createEntities(urlOrion, tool_life)
            
        if orion_output[1]["type"] == "MachiningData":
            ocb.createEntities(urlOrion, tool_life)

    orion_output = ocb.readEntities(urlOrion, id=articlenr+"_ToolLife")
    
    path_current = pathlib.Path(__file__).parent.resolve()
            
    with open(os.path.join(path_current, "Tool_life.json"), "w") as outfile:
        json.dump(tool_life, outfile)
    
   
if __name__ == "__main__":

    # Set the format for logging info
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # monitor Files
    event_handler = _CustomHandler()
    observer = Observer()
    observer.schedule(event_handler, path=local_path, recursive=True)
    observer.start()
    
    event_handler_tool = _CustomHandlerTool()
    observer_tool = Observer()
    observer_tool.schedule(event_handler_tool, path=local_path_tool, recursive=True)
    observer_tool.start()
    try:
        while True:
            time.sleep(10)

    finally:
        observer.stop()
        observer.join()
