import asyncio
import websockets
import http
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8765))

clients = set()
history = []  # последние 5 сообщений


# --- FIX: НЕ ЛОМАЕМ WebSocket handshake ---
async def process_request(path, request_headers):
    # если это WebSocket upgrade — НЕ трогаем
    upgrade = request_headers.get("Upgrade", "").lower()

    if upgrade == "websocket":
        return None  # <- ВАЖНО: пропустить handshake

    # иначе это обычный HTTP (Render health check)
    return (http.HTTPStatus.OK, [], b"OK")


async def broadcast(message):
    dead = set()

    for ws in clients:
        try:
            await ws.send(message)
        except:
            dead.add(ws)

    for ws in dead:
        clients.discard(ws)


async def handler(ws):
    print("Client connected")
    clients.add(ws)

    try:
        # отправляем историю
        for msg in history:
            await ws.send(msg)

        async for message in ws:
            print("Received:", message)

            history.append(message)
            if len(history) > 5:
                history.pop(0)

            await broadcast(message)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(ws)
        print("Client disconnected")


async def main():
    print(f"Running on ws://{HOST}:{PORT}")

    async with websockets.serve(
        handler,
        HOST,
        PORT,
        process_request=process_request
    ):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
