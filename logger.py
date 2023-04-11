from loguru import logger


output_format = "[{time:DD.MM.YY HH:mm:ss}] [{level}]: {message}"
logger_config = {
    "handlers": [{
        "sink": "debug.log",
        "format": output_format,
        "enqueue": True,
        "rotation": "5 MB",
        "compression": "zip",
        "level": "TRACE",
        "mode": "w",  # ! Убрать mode
    }]
}
logger.remove()
logger.configure(**logger_config)
