#!/usr/bin/env python

import asyncio
from websockets import connect
import sys

async def send(msg, uri):
    async with connect(uri) as websocket:
        await websocket.send(msg)
        #await websocket.recv()

message = ' '.join(sys.argv[1:])

asyncio.run(send(message, "ws://localhost:8765"))
