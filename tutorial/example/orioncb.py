#!/usr/bin/python3
import callrest as cr

import json
import os

def _procOrionVersion(urlBase):
    url = urlBase + '/version/'
    return cr.callRestApi(url, 'GET')

def _procOrionEntities(urlBase, method, data=None, id=None ,fiwareService=None, fiwareServicepath=None):
    url = urlBase + '/v2/entities/'
    if id:
       url = url + id
    if method =='PATCH':
        url = url + '/attrs'
    return cr.callRestApi(url, method, data=data ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def _procOrionSubscriptions(urlBase, method, data=None, id=None ,fiwareService=None, fiwareServicepath=None):
    url = urlBase + '/v2/subscriptions/'
    if id:
       url = url + id
    return cr.callRestApi(url, method, data=data ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def getVersion(urlBase):
    return _procOrionVersion(urlBase)

def createEntities(urlBase, data ,fiwareService=None, fiwareServicepath=None):
    return _procOrionEntities(urlBase, 'POST', data=data ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def readEntities(urlBase, data=None, id=None ,fiwareService=None, fiwareServicepath=None):
    return _procOrionEntities(urlBase, 'GET', data=data, id=id ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

#Only attrs (e.g counter)! No 'id' and 'Device' entry allowed in data
def updateEntities(urlBase, data, id,fiwareService=None, fiwareServicepath=None):
    return _procOrionEntities(urlBase, 'PATCH', data=data, id=id ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def deleteEntities(urlBase, id ,fiwareService=None, fiwareServicepath=None):
    return _procOrionEntities(urlBase, 'DELETE', id=id ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)
    
# def subscribeFromDir(urlBase, dir ,fiwareService=None, fiwareServicepath=None):
#     for entry in os.listdir(dir):
#         if os.path.isfile(os.path.join(dir, entry)):
#             print(entry)
#             with open(dir +'/' + entry) as f:
#                 subscribe(urlBase,json.load(f) ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

# def subscribeFromFile(urlBase, file ,fiwareService=None, fiwareServicepath=None):
#     with open(file) as f:
#         subscribe(urlBase,json.load(f) ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def createSubscriptions(urlBase, data ,fiwareService=None, fiwareServicepath=None):
    return _procOrionSubscriptions(urlBase, 'POST', data=data ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)
    
def readSubscriptions(urlBase, id=None ,fiwareService=None, fiwareServicepath=None):
    return _procOrionSubscriptions(urlBase, 'GET', id=id ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def updateSubscriptions(urlBase, data, id ,fiwareService=None, fiwareServicepath=None):
    return _procOrionSubscriptions(urlBase, 'PATCH', data=data, id=id ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

def deleteSubscriptions(urlBase, id ,fiwareService=None, fiwareServicepath=None):
    return _procOrionSubscriptions(urlBase, 'DELETE', id=id ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)

#Testing
if __name__ == "__main__":
    urlOrion = "http://localhost:1026"
    data={
        "id": "dummy1",
        "type": "Device",
            "counter": {
                "value": 0,
                "type": "Integer"
            }
    }
    
    dataSubs={
        "description": "subscription",
        "subject": {
            "entities" : [
                {
                    "idPattern" : ".*",
                    "type": "Device"
                }
            ],
            "condition": {
                "attrs" :["counter"]
            }
        },
        "notification": {
            "http": {
                "url": "http://quantumleap:8668/v2/notify"
            },
            "attrs": ["counter"],
            "metadata" : ["SourceTimestamp"]
        }
    }
    
    try:
        print("Deleting existing entities by id with status:", deleteEntities(urlOrion,data['id']))
        print("Generate entities with status", createEntities(urlOrion,data))
        print("Orion read:" ,readEntities(urlOrion))

        stat, resp = readSubscriptions(urlOrion)
        print('Read Subs: ', stat, resp)
        ids=[]
        for sub in resp:
            ids.append(sub['id'])
        print('Extract ids: ', ids)
        for e in ids:
            print("Delete Subs ", e, " with code: ", deleteSubscriptions(urlOrion,e))
        print('Create Subs with exitcode: ', createSubscriptions(urlOrion, dataSubs))
        stat, resp = readSubscriptions(urlOrion)
        print('Read Subs: ', stat, resp)
 
        patchData = data
        patchID = patchData.pop('id')
        patchData.pop('type')
        
        # for i in range(5):
        #     patchData['counter']['value'] = i
        #     updateEntities(urlOrion, patchData, patchID)
        #     print("Orion read:" ,readEntities(urlOrion))
            
        # print("Deleting existing entities by id with status:", deleteEntities(urlOrion,'dummy1'))

    except Exception as e:
        print("DOH!", e)