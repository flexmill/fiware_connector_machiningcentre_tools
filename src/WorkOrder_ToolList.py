# Reading of Work Order and Tool List from Wintool to create delta Tool List

import os
import time
import pandas as pd
import datetime
import pyodbc
import subprocess
import orioncb as ocb
import json #For general json file export
import pathlib
import os
import callrest as cr


def create_delta_toollist(urlOrion, path, machines, server, database, tool_dict, component_dict, cnxn, cursor, name_toollist, machine_number, article_num_act, article_num_new, status, date_scheduled, time_scheduled):
    setting1 = "1"
    setting2 = "1"

    cursor.execute("SELECT Nr FROM NCFolders WHERE Descript1=?", name_toollist)
    dummy_nr = cursor.fetchall()

    machine = machines[machine_number]

    for dummy in dummy_nr:
        cursor.execute("SELECT ToolListNr FROM NCObjectsFiles WHERE NCFolderNr=? AND NCObjectTypeNr=7", dummy)

        dummy_list_nr = cursor.fetchall()
        dummy_list_nr = str(dummy_list_nr).split(',')[0].replace('(', '').replace('[', '')

    ### get tools from actual toollist

    ident = machine + '_' + str(article_num_act) + '_' + setting1
    cursor.execute("SELECT Nr FROM ToolLists WHERE Ident=?", ident)
    toollist_nr = cursor.fetchall()

    if len(toollist_nr) == 0:
        ident = machine + '_' + str(article_num_act)
        cursor.execute("SELECT Nr FROM ToolLists WHERE Ident=?", ident)
        toollist_nr = cursor.fetchall()

    for i in toollist_nr:
        cursor.execute("SELECT ToolNr,Revolver,Station,Orientation FROM ToolList WHERE ToolListNr=?", i)
        tables_act = cursor.fetchall()

    ### get tools from new toollist

    ident = machine + '_' + str(article_num_new) + '_' + setting2
    cursor.execute("SELECT Nr FROM ToolLists WHERE Ident=?", ident)
    toollist_nr = cursor.fetchall()

    if len(toollist_nr) == 0:
        ident = machine + '_' + str(article_num_new)
        cursor.execute("SELECT Nr FROM ToolLists WHERE Ident=?", ident)
        toollist_nr = cursor.fetchall()

    for i in toollist_nr:
        cursor.execute("SELECT ToolNr,Revolver,Station,Orientation FROM ToolList WHERE ToolListNr=?", i)
        tables_new = cursor.fetchall()

        cursor.execute("SELECT APartID FROM ToolListAddOn WHERE ToolListNr=?", i)
        addons = cursor.fetchall()

    ### compare lists, only write difference for new list

    for i in tables_act:
        for j in tables_new:
            if i == j:
                tables_new.remove(j)


    # get delta tools from new toollist
    for tool in tables_new:
        tool_data = {}
        new_tool = str(tool).split(',')[0].replace('(', '')
        chann = str(tool).split(',')[1].replace('(', '')
        station = str(tool).split(',')[2].replace(')', '')
        orientation = str(tool).split(',')[3].replace(')', '')
        tool_data["id"] = new_tool
        tool_data["turret"] = chann
        tool_data["station"] = station
        tool_data["orientation"] = orientation
        tool_dict["tools"].append(tool_data)


    # get all components from toollist
    for addon in addons:
        component_data = {}
        new_addon = str(addon).split(',')[0].replace('(', '')
        cursor.execute("SELECT UNr FROM Parts WHERE ID=?", addon)
        component = cursor.fetchall()
        component = str(component[0]).replace("(", "").replace(",", "").replace(")", "")
        component_data["id"] = component
        component_dict["components"].append(component_data)
        cursor.execute("INSERT INTO ToolListAddOn (ToolListNr, APartID) VALUES (?,?)", dummy_list_nr, new_addon)
        cnxn.commit()

    i = 1

    order = {
        "id": "urn:ngsi-ld:WorkOrder:" + str(i),
        "type": "WorkOrder",
        "MachiningCentre": {"type":"MachiningCentre",
                    "value": machine_number},
        "status": {"type" : "status",
            "value" : status},
        "scheduledAt": {"type": "Date",
            "value": datetime.datetime.strptime(date_scheduled + time_scheduled, '%d.%m.%Y%H:%M:%S')},
        "warehouseId":{"type": "Warehouse",
                "value": "urn:ngsi-ld:Warehouse:01"},
        "workstationId": {"type": "Workstation",
                    "value": "urn:ngsi-ld:Workstation:" + machine_number},
        "materials": {"type": "List",
                    "value": []},
        "dateCreated":{"type": "Date",
                      "value": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

    }
    
    
    order["materials"]["value"].append(tool_dict)
    order["materials"]["value"].append(component_dict)
    
    id_update = {}
    id_update["MachiningCentre"] = {"type": "MachiningCentre",  "value": machine_number}
    id_update["status"] = {"type" : "status","value" : status}
    id_update["scheduledAt"] = {"type": "Date", "value": datetime.datetime.strptime(date_scheduled + time_scheduled, '%d.%m.%Y%H:%M:%S')}
    id_update["warehouseId"] = {"type": "Warehouse", "value": "urn:ngsi-ld:Warehouse:01"}
    id_update["workingStationId"] = {"type": "Workstation", "value": "urn:ngsi-ld:Workstation:" + machine_number}
    id_update["materials"] = {"type": "List", "value":  order["materials"]}
    id_update["dateCreated"] = {"type": "Date", "value": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}


    orion_output = ocb.readEntities(urlOrion, id="urn:ngsi-ld:WorkOrder:" + str(i)) #Output is a tuple with thte first an itneger with the error code as in integer 404
    if orion_output[0] == 404:
        print("entity new")
        ocb.createEntities(urlOrion, order)
    else:
        ocb.updateEntities(urlOrion, id_update, "urn:ngsi-ld:WorkOrder:" + str(i))
    
    
    path_current = pathlib.Path(__file__).parent.resolve()
    with open(os.path.join(path_current, "Work_Order.json"), "w") as outfile:
        json.dump(order, outfile)

    time.sleep(5)

    return order


def work_order(urlOrion, path, machines, server, database, name_toollist):
    
    active = True

    tool_dict = {"tools": []}
    component_dict = {"components": []}
    
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    
    for machine_number in machines:
    
        df = pd.read_excel(path, na_filter=False)

        df_mask = df['Unnamed: 3'] == int(machine_number)
        article_num_act = list(df[df_mask]['Unnamed: 2']).pop(-2)
        article_num_new = list(df[df_mask]['Unnamed: 2']).pop()
        date_scheduled = list(df[df_mask]['Unnamed: 8']).pop()
        time_scheduled = list(df[df_mask]['Unnamed: 9']).pop()
    
        df_status = df["Unnamed: 2"] == article_num_new
        status = list(df[df_status]['Unnamed: 10']).pop()
    
        if "B" in str(article_num_act):
            article_num_act = str(article_num_act[:-1])
    
        if "B" in str(article_num_new):
            article_num_new = str(article_num_new[:-1])
    
        if not status:
            create_delta_toollist(urlOrion, path, machines, server, database, tool_dict, component_dict, cnxn, cursor, name_toollist, machine_number, article_num_act, article_num_new, status, date_scheduled, time_scheduled)
            

