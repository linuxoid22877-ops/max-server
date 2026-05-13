import os
import asyncio
from http import HTTPStatus

from websockets.asyncio.server import serve

clients = set()


async def handler(ws):
    print("CLIENT CONNECTED")

    clients.add(ws)

    try:
        async for message in ws:
            print("MESSAGE:", message)

            dead = set()

            for client in clients:
                try:
                    await client.send(message)
                except:
                    dead.add(client)

            for d in dead:
                clients.discard(d)

    except Exception as e:
        print("ERROR:", e)

    finally:
        clients.discard(ws)
        print("CLIENT DISCONNECTED")


# ВАЖНО: отвечаем на обычные HTTP запросы
async def process_request(connection, request):
    headers = request.headers

    # если websocket upgrade -> пропускаем
    if headers.get("Upgrade", "").lower() == "websocket":
        return None

    # обычный HTTP запрос
    return connection.respond(
        HTTPStatus.OK,
        b"WebSocket server is running"
    )


async def main():
    port = int(os.environ.get("PORT", 8765))

    print("STARTING SERVER ON", port)

    async with serve(
        handler,
        "0.0.0.0",
        port,
        process_request=process_request
    ):
        print("SERVER STARTED")

        await asyncio.Future()


asyncio.run(main())
