##
# run this script on remote pc
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


#mount I:\Irkfish\ to /app/Irkfish in docker-compose.yml
#local_path = r'I:\Irkfish\Irkfish'
local_path = r'/app/Irkfish/Irkfish'
#sim_path = r'I:\Irkfish\Original_SIM'
sim_path = r'/app/Original_SIM'
#filename = r"\Irkfish"
filename = r"/app/Irkfish"
host = "10.10.65.1"

ocb_hostname = os.getenv("ORION_HOST", "orion") #set hostname in docker-compose file
ocb_port = os.getenv("ORION_HOST", "1026") #set port in docker-compose file
urlOrion = "http://{}:{}".format(ocb_hostname,ocb_port)
host = host.split(".")
del host[0]
del host[2]

machine = host[0] + host[1]

class _CustomHandler(FileSystemEventHandler):
    #def on_created(self, event):

        #writeFIWARE()


    def on_modified(self, event):

        writeFIWARE()


# write new line
def writeFIWARE():

    with open(local_path + filename + ".TXT", 'r') as file:
        # timestamp last part
        lastline = list(file).pop().split()

    with open(local_path + filename + ".TXT", 'r') as file:
        penultimate_article = list(file).pop(-2).split()

    with open(sim_path + "\RUNTIME_SIM.SPF", 'r') as sim_file:
        # timestamp SIM Part
        sim_line = list(sim_file).pop().split()


    timestamp = {"article_number": lastline[0], "date": lastline[1], "time": lastline[2], "charge": lastline[3],
                 "ideal_cycle_time": sim_line[4], "good_parts_counter": lastline[4]}


    datetime_timestamp = datetime.datetime.strptime(timestamp["date"] + timestamp["time"], '%d.%m.%Y%H:%M:%S')
    time_last_part = datetime.datetime.strptime(lastline[2], '%H:%M:%S')
    delta = datetime.timedelta(seconds=1)

    dt = datetime.date.today()

    MachiningCentre = {
        "id": timestamp["article_number"],
        "type": "MachiningData",
        "Batch": {
            "type": "Text",
            "value": timestamp["charge"]},
        "MachiningCentre": {
            "type": "Int",
            "value": int(machine)},
        "IdealCycleTime": {
            "type": "Second",
            "value": sim_line[4]},
        "MachiningDateStart": {
            "type": "Date",
            "value": str(datetime_timestamp.date())},
        "MachiningTimeStart": {
            "type": "Time",
            "value": str((time_last_part+delta).time())},
        "MachiningDateEnd": {
            "type": "Date",
            "value": str(datetime_timestamp.date())},
        "MachiningTimeEnd": {
            "type": "Time",
            "value": str(datetime_timestamp.time())},
        "GoodPartsCount": {
            "type": "Int",
            "value": timestamp["good_parts_counter"]},
        "GoodPartsDateStart": {
            "type": "Date",
            "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))},
        "GoodPartsDateEnd": {
            "type": "Date",
            "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))}
    }

    part_update = {}
    part_update["Batch"] = {"type": "Text", "value": timestamp["charge"]}
    part_update["MachiningCentre"] = {"type": "Int", "value": int(machine)}
    part_update["IdealCycleTime"] = {"type": "Second", "value": sim_line[4]}
    part_update["MachiningDateStart"] = {"type": "Date", "value": str(datetime_timestamp.date())}
    part_update["MachiningTimeStart"] = {"type": "Time", "value": str((time_last_part + delta).time())}
    part_update["MachiningDateEnd"] = {"type": "Date", "value": str(datetime_timestamp.date())}
    part_update["MachiningTimeEnd"] = {"type": "Time", "value": str(datetime_timestamp.time())}
    part_update["GoodPartsCount"] = {"type": "Int", "value": timestamp["good_parts_counter"]}
    part_update["GoodPartsDateStart"] = {"type": "Date", "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))}
    part_update["GoodPartsDateEnd"] = {"type": "Date", "value": str(datetime.datetime(dt.year, dt.month, dt.day).date() + datetime.timedelta(days=-1))}


    if penultimate_article[0] != timestamp["article_number"]:
        ocb.createEntities(urlOrion, MachiningCentre)

    else:
        ocb.updateEntities(urlOrion, part_update, timestamp["article_number"])
        
    print("Orion read:", ocb.readEntities(urlOrion, id=timestamp["article_number"]))

    path_current = pathlib.Path(__file__).parent.resolve()
    
    with open(os.path.join(path_current, "MachiningCentre.json"), "w") as outfile:
        json.dump(MachiningCentre, outfile)
    print(MachiningCentre)




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
    try:
        while True:
            time.sleep(1)

    finally:
        observer.stop()
        observer.join()

