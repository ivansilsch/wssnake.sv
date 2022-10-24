import asyncio
import websockets
import json
# import traceback
import routes


event_router = routes.EventRouter()


async def handler(websocket, path):
    try:
        async for message in websocket:
            event = json.loads(message)

            await event_router.call(
                method=event.get("method"),
                client=websocket,
                data=event.get("data"),
            )

    except websockets.exceptions.ConnectionClosed as e:
        print(e)
        print("Client disconnected")
        # for info in traceback.format_exception(e):
        #     # print(info)
        #     pass
    finally:
        # Removes the closed conection
        await event_router.call(
            method="disconnect",
            client=websocket,
            data=None
        )


async def main():
    async with websockets.serve(handler, "localhost", 8000):
        print("Listening for websockets...")
        await asyncio.Future()

asyncio.run(main())
