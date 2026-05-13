import asyncio
import os
from websockets.asyncio.server import serve

clients = set()

async def handler(websocket):
    print("CLIENT CONNECTED")

    clients.add(websocket)

    try:
        async for message in websocket:
            print("MESSAGE:", message)

            dead = set()

            for client in clients:
                try:
                    await client.send(message)
                except:
                    dead.add(client)

            for d in dead:
                clients.remove(d)

    except Exception as e:
        print("ERROR:", e)

    finally:
        clients.discard(websocket)
        print("CLIENT DISCONNECTED")


async def main():
    port = int(os.environ.get("PORT", 8765))

    print("STARTING ON PORT", port)

    async with serve(
        handler,
        "0.0.0.0",
        port
    ):
        print("WEBSOCKET SERVER STARTED")

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
