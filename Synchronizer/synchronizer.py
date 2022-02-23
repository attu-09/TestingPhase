import time
import json
from datetime import datetime

scriptStatus=None
with open("scriptStatus.json",'r') as file:
    scriptStatus=json.load(file)
    scriptStatus=scriptStatus['status']

def writeInScriptStatus(val):
    with open("scriptStatus.json",'w') as file:
        scriptStatus=json.load(file)
        scriptStatus['status']=val
        file.write(json.dumps(scriptStatus))
        scriptStatus=val

def checkProvisonState():
    while True:
        data=None
        with open("ento.conf",'r') as file:
            data=json.load(file)

        if data['device']['PROVISION_STATUS']==True:
            break
        else:
            try:
                #call for provisoning script
                pass
            except:
                #handle the exceptions
                pass
        time.sleep(60)

def mainLoop():
    while True:
        data=None
        with open("ento.conf",'r') as file:
            data=json.load(file)

        ON_TIME=data['device']['ON_TIME']
        OFF_TIME=data['device']['OFF_TIME']
        curTime=datetime.now().hour
        
        #Implement the raw logic of testFlag

        if ON_TIME<=curTime and curTime<OFF_TIME:
            if not scriptStatus:
                #Start both the services and write the status of the service in the status file
                writeInScriptStatus(True)
        else:
            if scriptStatus:
                #Stop the service 
                writeInScriptStatus(False)
        
        time.sleep(60)

if __name__=="__main__":
    checkProvisonState()
    #RUN Job Script/ Service
    mainLoop()

