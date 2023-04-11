

from enum import Enum


class Colors(Enum):
    grey = "\033[30m"
    lightred = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    lightblue = "\033[34m"
    purple = "\033[35m"
    cyan = "\033[36m"
    lightgrey = "\033[37m"
    red = "\033[91m"
    lightgreen = "\033[92m"
    blue = "\033[94m"
    pink = "\033[95m"
    lightcyan = "\033[96m"


class ColorFormatter:
    def __new__(cls, text: str, color: Colors) -> str:
        return f"{color.value}{text}\033[0m"
