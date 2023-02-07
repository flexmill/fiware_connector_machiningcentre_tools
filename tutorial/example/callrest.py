#!/usr/bin/python3
import requests

def _getHeaders(method=None, data=None ,fiwareService=None, fiwareServicepath=None):
    headers={}

    if fiwareService:
        headers.update({"fiware-service":fiwareService})
        sp = ''
        if  fiwareServicepath:   
            sp = sp + '/' + fiwareServicepath
        headers.update({"fiware-servicepath": sp})
            
    if method == 'POST' or method == 'PATCH':
        headers.update({'content-type': 'application/json'})

    return headers

def callRestApi(url, method, data=None ,fiwareService=None, fiwareServicepath=None):
    headers=_getHeaders(method=method ,fiwareService=fiwareService, fiwareServicepath=fiwareServicepath)
    r = requests.request(method, url, json=data, headers=headers)
    status = r.status_code
    try:
        response = r.json()
        return status, response
    except:
        return status    
