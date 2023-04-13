import pickle
import asyncio
from asyncio import StreamReader, StreamWriter
from collections import deque
from typing import Dict, List

import numpy as np

from logger import logger
from utils import (
    HOST,
    PORT,
    STARTUP_MESSAGE,
    RECENT_MESSAGES,
    COMMANDS,
    BACKUP_FILENAME
)
from models import User, Message
from color_formatter import Colors, ColorFormatter


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.users: Dict[str, List[User]] = {}
        self.history = deque(maxlen=RECENT_MESSAGES)

    async def start(self) -> None:
        self.load()
        try:
            server = await asyncio.start_server(self.authentication, self.host, self.port)
            logger.debug(f"Server started at {self.host}:{self.port}")
            async with server:
                await server.serve_forever()
        except Exception as ex:
            logger.debug(ex)
            raise ex

    async def authentication(self, reader: StreamReader, writer: StreamWriter) -> None:
        user = User(
            ip=writer.get_extra_info("peername")[0],
            port=writer.get_extra_info("peername")[1],
            reader=reader,
            writer=writer,
        )
        logger.debug(f"Connected user from {user.ip}:{user.port}")
        user.send(Message(
            text=ColorFormatter(STARTUP_MESSAGE, Colors.purple)
        ))
        await self.check_message(user)

    async def check_message(self, user: User):
        while True:
            message = await user.read()
            if not message:
                break
            logger.info(f"{message.sender}: {message.text}")
            if not message.text.startswith("/") and user.isLogged:
                message = Message(
                    sender=message.sender,
                    to="ALL",
                    text=message.text
                )
                await self.send(message)
                continue
            match message.text.split(" "):
                case COMMANDS.register.value, nickname, password, *_:
                    if not self.isLogged(user):
                        await self.register(user, nickname, password)
                case COMMANDS.login.value, nickname, password, *_:
                    if not self.isLogged(user):
                        await self.login(user, nickname, password)
                case COMMANDS.pm.value, nickname, *message:
                    if user.isLogged:
                        message = Message(sender=user.nickname, to=nickname, text=" ".join(message))
                        await self.pm(user, message)
                case _:
                    user.send(Message(
                        text=ColorFormatter("Command not found", Colors.red)
                    ))

    def isLogged(self, user: User) -> bool:
        if user.isLogged:
            user.send(Message(
                text=ColorFormatter("You have already logged", Colors.red)
            ))
            return True
        return False

    async def send(self, msg: Message) -> None:
        targets = list(np.concatenate(list(self.users.values())))
        for target in targets:
            message = Message(
                sender=msg.sender,
                to=msg.to,
                text=msg.text
            )
            if message.to == "ALL":
                if target.nickname != message.sender:
                    target.send(message)
                self.history.append(message)
            elif target.nickname == message.to:
                message.sender = f"PM {msg.sender}"
                target.send(message)

    async def pm(self, user: User, message: Message):
        if user.nickname == message.to:
            user.send(Message(
                text=ColorFormatter("Can not send message to yourself", Colors.red)
            ))
            return
        if message.to not in self.users.keys():
            user.send(Message(
                text=ColorFormatter("User with that nickname not exists", Colors.red)
            ))
            return
        await self.send(message)

    async def load_history_for(self, user: User):
        for message in self.history:
            user.send(message)
            await asyncio.sleep(0.1)

    async def login(self, user: User, nickname: str, password: str) -> None:
        compare_user = self.users.get(nickname, None)
        if compare_user is None or compare_user[0].password != password:
            user.send(Message(
                text=ColorFormatter("Login or password entered incorrectly", Colors.red)
            ))
            return
        user.isLogged = True
        user.nickname, user.password = compare_user[0].nickname, compare_user[0].password
        self.users[nickname].append(user)
        user.send(Message(
            text=ColorFormatter("You have logged in", Colors.lightgreen)
        ))
        logger.debug(f"{user.nickname} logged in, sessions: {len(self.users.get(user.nickname))}")
        await self.load_history_for(user)

    async def register(self, user: User, nickname: str, password: str) -> None:
        if nickname in self.users.keys():
            user.send(Message(
                text=ColorFormatter("That nickname already registered", Colors.red)
            ))
            return
        user.nickname = nickname
        user.password = password
        user.send(Message(
            text=ColorFormatter("You have registered successfully", Colors.lightgreen)
        ))
        user.isLogged = True
        self.users[nickname] = [user, ]
        logger.debug(f"User {user.nickname} registered")
        await self.load_history_for(user)

    def stop(self) -> None:
        with open(BACKUP_FILENAME, "wb") as file:
            for user_id in self.users:
                for user in self.users[user_id]:
                    user.reader = None
                    user.writer = None
            pickle.dump(self.users, file, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.history, file, pickle.HIGHEST_PROTOCOL)
        logger.debug("Server stopped, users and history saved")

    def load(self) -> None:
        try:
            with open(BACKUP_FILENAME, "rb") as f:
                self.users = pickle.load(f)
                self.history = pickle.load(f)
        except FileNotFoundError:
            logger.debug("Dump file not found")
        else:
            logger.debug("Server loaded, users and history restored")


if __name__ == "__main__":
    server = Server()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        server.stop()
