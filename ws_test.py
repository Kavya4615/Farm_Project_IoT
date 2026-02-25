import asyncio
import websockets

async def test():
    async with websockets.connect("ws://10.23.66.82:8765") as ws:
        print("Connected!")
        while True:
            msg = await ws.recv()
            print("Received:", msg)

asyncio.run(test())
