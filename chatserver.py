import asyncio
import websockets
import os
from collections import deque

# Порт для большинства хостингов (Render, Railway и т.д.)
PORT = int(os.environ.get("PORT", 8080))

clients = set()
history = deque(maxlen=100)  # последние 100 сообщений

async def handler(ws):
    clients.add(ws)
    print(f"✅ Client connected | Total: {len(clients)}")

    # Отправляем историю
    for msg in history:
        try:
            await ws.send(msg)
        except:
            pass

    try:
        async for msg in ws:
            print("📨 MSG:", msg)
            history.append(msg)

            # Рассылаем всем кроме отправителя
            dead = set()
            for client in list(clients):
                if client != ws:
                    try:
                        await client.send(msg)
                    except:
                        dead.add(client)

            for d in dead:
                clients.discard(d)

    finally:
        clients.discard(ws)
        print(f"❌ Client disconnected | Total: {len(clients)}")

async def main():
    print(f"🚀 Chat server started on port {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()  # работает вечно

if __name__ == "__main__":
    asyncio.run(main())
