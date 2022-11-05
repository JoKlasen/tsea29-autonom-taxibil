import serial
import subprocess

# sendMessage() stuff
import asyncio
from websockets import connect
import sys

async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)

with serial.Serial('/dev/ttyUSB1', 57600) as ser:
	while(True):
		line = ser.readline().decode("utf-8")[1:-1] 
		print(line)
		asyncio.run(send(line, "ws://localhost:8765"))
