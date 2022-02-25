import time
import json
from datetime import datetime
import requests

global scriptStatus
scriptStatus=False
path = "/etc/entomologist/"
def entoDataWriter(parent,key,value):
    data=None
    with open(path + "ento.conf",'r') as file:
        data=json.load(file)
    data[parent][key]=value
    with open(path + "ento.conf",'w') as file:
        file.write(json.dumps(data,indent=4))

def testDevice(duration):
    if not scriptStatus:
        #start the services
        subprocess.call(["systemctl","restart","cam"])
        subprocess.call(["systemctl","restart","upload"])

    while duration:
        print("Testing the device")
        duration-=1
        time.sleep(1)
    print("Testing Complete")
    entoDataWriter('device','TEST_FLAG','False')

def writeInScriptStatus(val): 
    data=None
    with open(path + "scriptStatus.json",'r') as file:
        data=json.load(file)
    with open(path + "scriptStatus.json",'w') as file:
        data['status']=val
        file.write(json.dumps(data,indent=2))
        scriptStatus=val

def checkProvisonState():
    print("checking Provison state")
    while True:
        data=None
        with open(path + "ento.conf",'r') as file:
            data=json.load(file)

        if data['device']['PROVISION_STATUS']=='True':
            print("Device Provisoned")
            break
        else:
            print("Trying For Provison")
            try:
                #call for provisoning script
                subprocess.call(["python3","/usr/sbin/provision/boot.py"])
                p = subprocess.Popen("ifconfig", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()
                device=data['device']["SERIAL_ID"] #should be getting from the conf file
                #ip="64.2.232.22" #should be find by pratyush bhaiya
                url="https://en0xlpnmw1.execute-api.us-east-1.amazonaws.com/send"
                param={'device':device,'ip':str(output)}
                resp=requests.get(url,params=param)
            except Exception as e:
                with open (path + "Error.txt", "a") as file:
                    file.write(str(e))

        time.sleep(10)

def mainLoop():
    while True:
        data=None
        with open(path + "ento.conf",'r') as file:
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
                subprocess.call(["systemctl","restart","cam"])
                subprocess.call(["systemctl","restart","upload"])
                writeInScriptStatus(True)
        else:
            print("Timing not matching")
            if scriptStatus:
                #Stop the service
                subprocess.call(["systemctl","stop","cam"])
                subprocess.call(["systemctl","stop","upload"])
                writeInScriptStatus(False)
        
        time.sleep(3)

if __name__=="__main__":
    entoDataWriter('device','TEST_FLAG','False')
    writeInScriptStatus(False)
    checkProvisonState()
    print("Running Job service")#RUN Job Service
    subprocess.call(["systemctl","restart","jobreceiver"])
    mainLoop()

