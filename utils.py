from enum import Enum


class COMMANDS(Enum):
    register = "/register"
    login = "/login"
    pm = "/pm"


HOST = "127.0.0.1"
PORT = 8000
STARTUP_MESSAGE = """
Available commands:
/register <nickname> <password>
/login <nickname> <password>
/pm <nickname> <text>
"""
RECENT_MESSAGES = 20
BACKUP_FILENAME = "backup.pkl"
