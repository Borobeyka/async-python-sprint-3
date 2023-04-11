import asyncio
import pickle

from aioconsole import ainput
from utils import (
    HOST,
    PORT
)

from color_formatter import Colors, ColorFormatter
from models import Message


class Client:
    def __init__(self, server_host=HOST, server_port=PORT):
        self.server_host = server_host
        self.server_port = server_port

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(
            self.server_host,
            self.server_port
        )
        await asyncio.gather(
            self.receive_messages(),
            self.send_to_server()
        )

    async def receive_messages(self):
        server_message = None
        while server_message != "quit":
            server_message = await self.get_from_server()
            print(ColorFormatter(
                f"[{server_message.sender}]:",
                Colors.cyan
            ), end=" ")
            print(f"{server_message.text}")

    async def get_from_server(self) -> Message:
        return pickle.loads(await self.reader.read(1024))

    async def send_to_server(self) -> None:
        while True:
            response = await ainput("")
            self.writer.write(
                pickle.dumps(Message(text=response))
            )
            await self.writer.drain()


if __name__ == "__main__":
    asyncio.run(Client().connect())
