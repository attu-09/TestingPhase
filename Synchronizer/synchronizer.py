import time
import json
from datetime import datetime

global scriptStatus
scriptStatus=False

def entoDataWriter(parent,key,value):
    data=None
    with open("ento.conf",'r') as file:
        data=json.load(file)
    data[parent][key]=value
    with open("ento.conf",'w') as file:
        file.write(json.dumps(data,indent=4))

def testDevice(duration):
    if not scriptStatus:
        #start the services
        pass 

    while duration:
        print("Testing the device")
        duration-=1
        time.sleep(1)
    print("Testing Complete")
    entoDataWriter('device','TEST_FLAG','False')

def writeInScriptStatus(val): 
    data=None
    with open("scriptStatus.json",'r') as file:
        data=json.load(file)
    with open("scriptStatus.json",'w') as file:
        data['status']=val
        file.write(json.dumps(data,indent=2))
        scriptStatus=val

def checkProvisonState():
    print("checking Provison state")
    while True:
        data=None
        with open("ento.conf",'r') as file:
            data=json.load(file)

        if data['device']['PROVISION_STATUS']=='True':
            print("Device Provisoned")
            break
        else:
            print("Trying For Provison")
            try:
                #call for provisoning script
                pass
            except:
                #handle the exceptions
                pass
        time.sleep(3)

def mainLoop():
    while True:
        data=None
        with open("ento.conf",'r') as file:
            data=json.load(file)

        if data['device']['TEST_FLAG']=='True':
            duration=int(data['device']['TEST_DURATION'])*60
            testDevice(duration)
        
        ON_TIME=int(data['device']['ON_TIME'])
        OFF_TIME=int(data['device']['OFF_TIME'])
        curTime=datetime.now().hour
        
        #Implement the raw logic of testFlag

        if ON_TIME<=curTime and curTime<OFF_TIME:
            print("Device Running")
            if not scriptStatus:
                #Start both the services and write the status of the service in the status file
                writeInScriptStatus(True)
        else:
            print("Timing not matching")
            if scriptStatus:
                #Stop the service 
                writeInScriptStatus(False)
        
        time.sleep(3)

if __name__=="__main__":
    entoDataWriter('device','TEST_FLAG','False')
    writeInScriptStatus(False)
    checkProvisonState()
    print("Running Job service")#RUN Job Service
    mainLoop()

