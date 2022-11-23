import serial
import subprocess
import asyncio
from websockets import connect
import sys

async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)

def start_communication(port):
    with serial.Serial(port, 57600) as ser:
        while(True):
            line = ser.readline().decode("utf-8")[1:-1]
            print(line)
            asyncio.run(send(line, "ws://localhost:8765"))

serial_port = ' '.join(sys.argv[1:])
start_communication(serial_port)
