#!/usr/bin/env python

import asyncio
from websockets import serve
import time
import datetime
import serial
import sys

serial_port = ' '.join(sys.argv[1:])

def timestamp():
	timestamp = time.time()
	date_time = datetime.datetime.fromtimestamp(timestamp)
	str_date_time = date_time.strftime("%d/%m %H:%M:%S")
	return str_date_time

CLIENTS = []

async def send(websocket, message):
    try:
        await websocket.send(message) 
    except Exception as e:
        print("========== ERROR 1 ===========")
        print("Connection lost.")
        print("Sending brake signal to Control Unit.")
        sendToAVR("keyspressed:forward=0:left=0:back=1:right=0:")
        print("Sent brake signal.")
        print("Exiting program...")
        exit()

print("Starting server...")

ser = serial.Serial (serial_port, 57600)
def sendToAVR(message):
    message_type = message.split(':')[0]
    #print("Message Type: " + message_type)
    
    if (message_type == 'keyspressed'):
        print("Got 'keyspressed' command, sending to Control Unit")
        message = message + "\0"
        print(message)
        ser.write(message.encode());
    
async def sendAll(websocket):
    #print(websocket)
    
    async for message in websocket:
        print(timestamp() + " " + message)
        sendToAVR(message)
        if websocket not in CLIENTS:
            if "[webapp]" in message:
                CLIENTS.append(websocket)
        try:
            for socket in CLIENTS:
                await send(socket, message)
        except Exception as e:
            print("========== ERROR 2 ===========")
            print("Connection lost.")
            print("Sending brake signal to Control Unit.")
            sendToAVR("keyspressed:forward=0:left=0:back=1:right=0:")
            print("Sent brake signal.")
            print("Exiting program...")
            exit()

async def main():
    async with serve(sendAll, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())