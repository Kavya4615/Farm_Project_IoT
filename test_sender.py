import asyncio
import websockets
import random
import time

HOST = "0.0.0.0"
PORT = 8765

clients = set()

async def handler(websocket):
    print("Client connected")
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        print("Client disconnected")
        clients.remove(websocket)

async def send_data():
    while True:
        if clients:
            soil_flag = random.choice([0, 1])
            soil_value = round(random.uniform(30, 80), 2)
            air_humidity = round(random.uniform(40, 90), 2)

            msg = f"{soil_flag},{soil_value},{air_humidity}"
            print("Sending:", msg)

            await asyncio.gather(*(c.send(msg) for c in clients))

        await asyncio.sleep(1)

async def main():
    async with websockets.serve(handler, HOST, PORT):
        print(f"Test WebSocket running on ws://{HOST}:{PORT}")
        await send_data()

asyncio.run(main())
