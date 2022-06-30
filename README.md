# fiware_connector_c200
Fiware connector to machining centres and specifically to index c200

# Connector to machining centres
The machining data of the machining centre C200 is read via a self developed interface called “Irkfish”. For each machined part following data are read from the machining centre by a direct connection to the NC code running: article number; batch number; date and time stamp of machining start time per part; date and time stamp of machining stop time per part. With these data KPIs as well as the status of the machining centre can be analyzed. These data from the machining centre are put into a smart data model to be then sent to a local instance of the FIWARE context broker.  

## Usage
For the simulated of the machining centre that shall be read in copy_irkfish_sim.py following variables have to be configured according to individual machining centre simulator:
local_path = r'xxx' ... local path where simulation data shall be saved to
rem_path = r'xxx'  ... path of the machining centre simulator
filename = r"xxx" ... Filename of the data file with the simulation data

For the use of the data from the machining centre in copy_irkfish.py following parameters have to be configured according to individual machining centre:
host = 'xxx' ... adress of the machining centre
port = 'xx' ... port of the machining centre
username = 'xxx' ... username for access
password = 'xxx' ... password for access

local_path = r'xxx' ... local path where machining data shall be copied to for further use
ori_local_path = r''  ... local path where original data shall be saved to
rem_path = 'xxx' ... path of  machining centre
filename = "xxx"  ... filename of machining data

# Connector to ERP System
FIWARE connector to ERP system Dynamics D365: The same software package contains a connector to the ERP system to read number of good parts that are produced in order to be able to analyze the required KPIs. These data are then also sent to the context broker in the same data model as described before

## Usage
To read required data from the ERP system and in this case the required good parts following variables have to be configured
server = 'xxx' ... servername of ERP system and databse
database = 'xxx' ... name of database
username_sql = 'xxx' ... username for database access
password_sql = 'xxx'  ... password for database access

# Run irkfish for data connection to machining centre
To start reading data from the machining centre run irkfish.py and configure following variables:
local_path = r'xxx'  ... local path where machining data is saved
sim_path = r'xxx' .... local path where simulataion data is saved
filename = r"xxx" ... filename of machining centre data
host = "xxx" ... adress of machining centre
