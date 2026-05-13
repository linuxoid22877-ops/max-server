import asyncio
import websockets
import http

HOST = "0.0.0.0"
PORT = 8765

clients = set()
history = []  # храним только 5 последних сообщений


# --- FIX: HTTP/HEAD requests (health checks) ---
async def process_request(path, request_headers):
    # Render / прокси могут слать HEAD / GET /
    # просто отвечаем OK, чтобы сервер не падал
    return http.HTTPStatus.OK, [], b"OK"


async def broadcast(message):
    dead = set()

    for ws in clients:
        try:
            await ws.send(message)
        except:
            dead.add(ws)

    # чистим мёртвые соединения
    for ws in dead:
        clients.discard(ws)


async def handler(ws):
    print("Client connected")
    clients.add(ws)

    try:
        # отправляем историю новому клиенту
        for msg in history:
            await ws.send(msg)

        async for message in ws:
            print("Received:", message)

            # сохраняем только 5 последних
            history.append(message)
            if len(history) > 5:
                history.pop(0)

            # рассылаем всем
            await broadcast(message)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(ws)
        print("Client disconnected")


async def main():
    print(f"Server running on ws://{HOST}:{PORT}")

    async with websockets.serve(
        handler,
        HOST,
        PORT,
        process_request=process_request  # <-- ВОТ ГЛАВНЫЙ ФИКС
    ):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
