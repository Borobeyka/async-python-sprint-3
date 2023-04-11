from __future__ import annotations
import pickle

from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from typing import Optional

from color_formatter import ColorFormatter


@dataclass(kw_only=True)
class Message:
    sender: Optional[str] = "SERVER"
    to: Optional[str] = None
    text: ColorFormatter | str


@dataclass(kw_only=True)
class User:
    ip: str
    port: int
    reader: StreamReader
    writer: StreamWriter

    nickname: Optional[str] = None
    password: Optional[str] = None
    isLogged: bool = False

    def send(self, message: Message) -> None:
        self.writer.write(pickle.dumps(message))

    async def read(self) -> str:
        message = pickle.loads(await self.reader.read(1024))
        message.sender = self.nickname
        return message
