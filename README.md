# FlexMill Fiware Connector Machining Centre
Python Code for connecting data from machining centre to Fiware

FlexMill Fiware Connector Machining Centre is a project that shall allow machining data acces by using NC code and python and Fiware. As well as connection to ERP system to read historical data of machined parts and to read work orders that are used to plan the tool logistics within the AMR control project.
In this repository the code for Fiware Connector Machining Centre is stored.

This project is part of [DIH2](http://www.dih-squared.eu/).

This project is part of [FIWARE](https://www.fiware.org/). For more information check the [FIWARE Catalogue](https://github.com/Fiware/catalogue/).

# Background
The complete industrial engineering and production process starting with a 3D model and up to the final part shall be fully automatized including variations of parts and its features. One group of products at RO-RA are adapter ends of Aerostruts, which can vary by geometry, size, material and batch size. At the beginning of this process these parts shall be described by various parameters and this data set of parameters shall automatically trigger all subsequent processes. These processes use different technologies such as CAD, ERP, CAM, NC-Simulation, CAQ (control plan), tool management, AMR, CMM. Further on the FIWARE platform shall be used to handle and process the generated data in each step and to trigger these subprocesses. It shall be emphasized here that the AMR is key for the reduction of non-value adding expenses especially for small batch sizes and will be used as a key part of this experiment. The AMR will be used to autonomously deliver the right tooling to the right machining centres at the right time orchestrated by FIWARE. This is key in agile production so that the system can adapt to variations of parts, which cause variations in subprocesses and hence the AMR can adapt to these variations without complex reconfigurations and programming. By implementing such a digital platform we shall be able to have a traceability and seamless interoperability of complex systems including AMR. We shall be able to easily reconfigure the system by parameters, and we shall be able to efficiently manage, visualize and analyse data and monitor and optimise features at multiple factory levels.

# Design thoughts:
- Interface to machining centres shall be implemented without additional licenses such as OPC UA
- Interface must be as simple as possible and adaptable for different machining centre types independent of their systems.

# Connector to machining centres
The machining data of the machining centre C200 is read via a self developed interface called “Irkfish”. For each machined part following data are read from the machining centre by a direct connection to the NC code running: article number; batch number; date and time stamp of machining start time per part; date and time stamp of machining stop time per part. Additionally tool life is read as well for the automated tool logistics of replacement tools. With these data KPIs as well as the status of the machining centre can be analyzed. These data from the machining centre are put into a smart data model to be then sent to a local instance of the FIWARE context broker.  

## Build and Install
1. Integrate the spf files within Irkfish_NC-Code to your current NC code of interest to export the necessary machining data
2. Set the paramteters for the connection to the machining centre such as hostname, prt, username and password within the file copy_irkfish.py to establish the connection to the machining centre.
3. Set the parameters for the paths and and file names of the data within the file copy_irkfish.py to be stored to in order to be used for further analysis
4. Set the parameters for the connection to the ERP system database within the file copy_irkfish.py such as server, database, username and password in order to be able to read data for the good parts count as well as ideal cycle times of parts.
5. Set the parameters for the local paths within irkfish.py where machining centre data is exported from copy_irkfish.py Set list of machining centre names that shall be connected. Set parameters for work order destinations that shall be read and parameters to connect to Software Wintool for the data of tool information such as server, database and name of specific tool lists.
6. Open irkfish.py in any IDE supporting Python
5. Compile and run
6. Create a Docker Image as shown in folder docker and docs and run docker image to set up Fiware container.

Summary of parameters to be set:

copy_irkfish.py:
host = 'xxx' #Machining centre adress
port = 'xx' # Port of machining centre
username = 'xxx' #Username of machining centre
password = 'xxx' #Password of machining centre
local_path = 'xxx' ... local path where simulation data shall be saved to
ori_local_path = 'xxx' #local path where original data shall be saved to 
rem_path = 'xxx'  ... path of the machining centre 
filename = 'xxx' ... Filename of the machining data
local_path_tool_life = 'xxx' #local path where tool life data shall be saved to 
filename_tool_life = 'xxx' #file name where tool life data shall be saved to 
server = 'xxx' #Sever name of ERP system to read good parts and ideal cycle time data  
database = 'xxx' #Database name of ERP system to read good parts and ideal cycle time data 
username_sql = 'xxx' #User name of database 
password_sql = 'xxx' #Password of database

irkfish.py:
local_path = 'xxx' #Path to file of machining centre runtimes that were exported by IRKSFISH_A.SPF, IRKSFISH_E.SPF and irkfish_copy.py
local_path_tool = 'xxx' #Path to file of machining centre tool lifes that were exported by TOOL_LIFE.SPF and irkfish_copy.py
sim_path = 'xxx' #Path to simulated runtimes for definition of ideal cycle times
machines = ['xxx', 'xxx,'] #List of machining centres that shall be observed 
path_wo = 'xxx' #Path to work order file that shall be read
machines_wo = {'xxx': 'xxx'} #Dictionary of machines for which work orders shall be performed
server = 'xxx' #Server where Wintool is running
database = 'xxx' #Database of tool in Wintool
name_toollist = 'xxx' #Name of specific tool List


# Workflow
The project reads data from machining centres to analyze KPI data as well as read work order instructions that are required for the software package AMR Control as well as tool life data of actul tools within the machining centres in order to get data for the planning of tool replacement loigistics.
This code only rteads data and th more specific workflow where human interaction is required is described in AMR-Control.


