#!/usr/bin/env python

import asyncio
from websockets import serve
import time
import datetime
import serial
import sys
import subprocess

# take command line arguments
serial_port = ' '.join(sys.argv[1:])

# Define which commands should be sent where.
commands_app = ["db", "tm", "DEBUG"]
commands_cv = ["mi"]
commands_control = ["kp", "es", "sm", "spp", "stp", "er", "tm", "td"]

# Get timestamp
def timestamp():
	timestamp = time.time()
	date_time = datetime.datetime.fromtimestamp(timestamp)
	str_date_time = date_time.strftime("%d/%m %H:%M:%S")
	return str_date_time

# array of connected clients
CLIENTS = []

# Send message to client
async def send(websocket, message):
    message_type = message.split(':')[0]

    try:
        if (message_type in commands_app):
            print("To App-Module: ", message)
            await websocket.send(message) 
    
    except Exception as e:
        print("=========== ERROR ============")
        print(e)
        print("Connection lost. Sending Break Signal to Control Unit.")
        sendToAVR("kp:f=0:l=0:b=1:r=0:")
        print("==============================")

# Start serial connection
ser = serial.Serial (serial_port, 57600)
def sendToAVR(message):
    message_type = message.split(':')[0]
    
    # remove first character from string
    message = message[1:]


    if (message_type in commands_control):
        message = message + '\n';
        print("To Control-Module: ", message)
        ser.write(message.encode())

# TODO IMPLEMENT SENDING TO CV MODULE
def sendToCV(message):
    message_type = message.split(':')[0]
    message_parts = message.split(':')
    print("Before CV-Module: ", message)
    if (message_type in commands_cv):
        print("To CV-Module: ", message)
        if (message_type == 'mi'):
            from_location = message_parts[1].split('=')[1]
            pickup_location = message_parts[2].split('=')[1]
            drop_location = message_parts[3].split('=')[1]

            #command_string = '/usr/bin/python3 /home/g13/git/communication-module/main.py ' + from_location + ' ' + pickup_location + ' ' + drop_location
            command_string = '/home/g13/git/communication-module/main.py ' + from_location + ' ' + pickup_location + ' ' + drop_location

            print("mi Command: " + command_string)
            subprocess.call(command_string, shell=True)

# Send message to all connected clients§
async def sendAll(websocket):
    async for message in websocket:
        print(timestamp() + " " + message)
        
        sendToAVR(message)

        sendToCV(message)

        if websocket not in CLIENTS:
            if "[webapp]" in message:
                CLIENTS.clear()
                CLIENTS.append(websocket)
        
        try:
            for socket in CLIENTS:
                await send(socket, message)
        except Exception as e:
            print("=========== ERROR ============")
            print(e)
            print("Connection lost. Sending Break Signal to Control Unit.")
            sendToAVR("kp:f=0:l=0:b=1:r=0:")
            print("==============================")

# Start server
async def main():
    async with serve(sendAll, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

print("Starting server...")
asyncio.run(main())
