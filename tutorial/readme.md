# FlexMill Fiware Connector Machining Centre
Tutorial using artificial data from machining centres and ERP system to show the workflow of this connector.

Perform the build ans install procedure as described in the [readme file](https://github.com/flexmill/fiware_connector_machiningcentre_tools/blob/main/README.md) starting with step 6. Step 1-5 are required to set the specific connection to the individual machining centres and ERP systems that are in place at each individual company.

## Workflow Machining Centre Data
1. Compile and run the script irkfish.py in [tutorial/example](https://github.com/flexmill/fiware_connector_machiningcentre_tools/tree/main/tutorial/example)
2. The required data is artificial machining data an can be found in the corresponding subfolders: [tutorial/example](https://github.com/flexmill/fiware_connector_machiningcentre_tools/tree/main/tutorial/example)
3. To simulate the operation of the machining centre increase the time of the [file](https://github.com/flexmill/fiware_connector_machiningcentre_tools/blob/main/tutorial/example/Original/IRKFISH_1045_A.SPF) for 1 minute and the same for [file](https://github.com/flexmill/fiware_connector_machiningcentre_tools/blob/main/tutorial/example/Original/IRKFISH_1045.SPF) that simulates the start and end of a machined part.
4. The software will then read the new data and create the correpsonding data in the Fiware context broker.
5. The further processing of data is then done by [Fiware-databroker-console](https://github.com/flexmill/Fiware-databroker-console)

## Workflow Tool Life
1. Compile and run the script irkfish.py in [tutorial/example](https://github.com/flexmill/fiware_connector_machiningcentre_tools/tree/main/tutorial/example)
2. The required data is artificial tool life data an can be found in the corresponding subfolders: [Tool_Life](https://github.com/flexmill/fiware_connector_machiningcentre_tools/tree/main/tutorial/example/Tool_Life)
3. To simulate the tool life data that is calculated by the machining centre decrease the number of the last column in the [file](https://github.com/flexmill/fiware_connector_machiningcentre_tools/blob/main/tutorial/example/Tool_Life/TOOL_LIFE_1045.csv) of any tool that is listed. This is the time counter of the rest of the tool life and has to be changed manually to simulate the operation of the machining centre.
4. The software will then read the new data and create the correpsonding data in the Fiware context broker.
5. The further processing of the tool life data and the further loigistics using the AMR for tool delivery in time will then be further done by [AMRControl](https://github.com/flexmill/AMRControl)
