##
#copy file to server


import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import time
import goodpartscounter as gpc


local_path = r'ccc' #local path where simulation data shall be saved to
rem_path = r'xxx' #path of the machining centre simulator
filename = r"xxx" #Filename of the data file with the simulation data


server = 'RoRaBI.database.windows.net' #servername of ERP system and databse
database = 'RORABIProd'  #name of database
username = 'xxx' #username for database access
password = 'xxx' #password for database access
machine = "1065"


class _CustomHandler(FileSystemEventHandler):
    def on_created(self, event):
        # path cnc machine
        shutil.copy(rem_path + filename + ".SPF", local_path)
        good_parts_counter = gpc.getCounter(machine, server, database, username, password)
        # print(good_parts_counter)
        with open(local_path + filename + '.SPF', 'r') as a_ori:
            text = a_ori.read().split('\t')
            #text[5] = good_parts_counter
            new_line = text[0] + '\t' + text[1] + '\t' + text[2] + '\t' + text[3] + '\t' + text[4] + '\t' + str(good_parts_counter)
            print(text[0] + '\t' + text[1] + '\t' + text[2] + '\t' + text[3] + '\t' + text[4] + '\t' + str(good_parts_counter))

        with open(local_path + filename + '.SPF', 'w') as a_ori:
            a_ori.write(new_line)

    # def on_modified(self, event):
    #     # path cnc machine
    #     shutil.copy(rem_path + filename + ".SPF", local_path)
    #     good_parts_counter = gpc.getCounter(machine, server, database, username, password)
    #     # print(good_parts_counter)
    #     with open(local_path + filename + '.SPF', 'r') as a_ori:
    #         text = a_ori.read().split('\t')
    #         #text[5] = good_parts_counter
    #         new_line = text[0] + '\t' + text[1] + '\t' + text[2] + '\t' + text[3] + '\t' + text[4] + '\t' + str(good_parts_counter)
    #         print(text[0] + '\t' + text[1] + '\t' + text[2] + '\t' + text[3] + '\t' + text[4] + '\t' + str(good_parts_counter))
    #
    #     with open(local_path + filename + '.SPF', 'w') as a_ori:
    #         a_ori.write(new_line)


if __name__ == "__main__":

    # Set the format for logging info
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # monitor Files
    event_handler = _CustomHandler()
    observer = Observer()
    observer.schedule(event_handler, path=rem_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)


    finally:
        observer.stop()
        observer.join()
