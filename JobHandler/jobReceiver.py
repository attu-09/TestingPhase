#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from datetime import datetime
import os
import time
import json
import threading

now=datetime.now()
time_stamp=now.strftime("%m/%d/%Y, %H:%M:%S")

with open(f"ento.conf",'r') as file:
	data=json.load(file)

MQTT_BROKER = data["device"]["ENDPOINT_URL"]
SERIAL_ID = data["device"]["SERIAL_ID"]
PORT = 8883
MQTT_KEEP_INTERVAL = 44
JOB_CLIENT = f'JobReciverClient-{SERIAL_ID}'
JOB_TOPIC = f'cameraDevice/job/{SERIAL_ID}'
QoS = 0

rootCA = '/etc/entomologist/cert/AmazonRootCA1.pem'
cert = '/etc/entomologist/cert/certificate.pem.crt'
privateKey = '/etc/entomologist/cert/private.pem.key'


def updateData(name,keyValue):
        data={}
        with open(f"/etc/entomologist/ento.conf",'r') as file:
            data=json.load(file)
            dataa=data[name]
        with open(f"/etc/entomologist/ento.conf",'w') as file:
            dataa.update(keyValue)
            data.update({name:dataa})
            json.dump(data,file,indent=4,separators=(',', ': '))


def on_message(client, userdata, message):
	
	jobconfig = json.loads(message.payload.decode('utf-8'))
	print(f"Job Recieved\n{jobconfig}")


	t_job = threading.Thread(name='parse', target=parse,args=(jobconfig,client))
	t_job.start()

def parse(jobconfig,client):
    try:

        if jobconfig['deviceId'] == SERIAL_ID:


            
            onTime=jobconfig['device']['Device-Up-Time']
            onDuration=jobconfig['device']['Device-On-Time']
                        
            updateData("device",{"ON_TIME":onTime})
            updateData("device",{"ON_DURATION":onDuration})
            

    except:
        print("Job Failed")



def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Job Client Connected")
		
	else:
		print("Bad connection: Job Client")

def start_recieving_job():

	global jobClient

	jobClient = mqtt.Client(JOB_CLIENT)

	jobClient.tls_set(rootCA, cert, privateKey)

	jobClient.on_connect = on_connect
	jobClient.on_message = on_message

	jobClient.connect(MQTT_BROKER, PORT, MQTT_KEEP_INTERVAL)

	jobClient.subscribe(JOB_TOPIC, QoS)

	jobClient.loop_forever()

def restart_recieving_job():

	global jobClient

	jobClient.disconnect()

	print(f"{'-'*20} Restarting Job Reciever {'-'*20}")

	time.sleep(3)

	start_recieving_job()


if __name__ == '__main__':
	
	start_recieving_job()