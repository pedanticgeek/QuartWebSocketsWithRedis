# Imports for local logging
import traceback
import os
import logging


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.formats = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_logger(name: str, file: str | None, level: str):
    """Creates a logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", level)))
    # Create formatter and apply it to both handlers
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if file:
        if not os.path.exists(os.getcwd() + "/logs"):
            os.mkdir(os.getcwd() + "/logs")
            # Create a log file handler to write all logs
        if os.path.exists(os.getcwd() + f"/logs/{file}.log"):
            os.remove(os.getcwd() + f"/logs/{file}.log")
        file_logger = logging.FileHandler(os.getcwd() + f"/logs/{file}.log")
        file_logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", level)))
        file_logger.setFormatter(CustomFormatter(fmt))
        logger.addHandler(file_logger)
    # Create a console log handler to handle only ERROR level logs
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(CustomFormatter(fmt))
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


class Logger:
    def __init__(self, name: str, filename: str | None = None, level: str = "INFO"):
        self.logger = create_logger(name, filename, level)

    def log(self, exception: Exception, **_kwargs):
        getattr(self.logger, exception["level"])(exception["message"])
        return exception["message"]

    def info(self, text: str, **_kwargs):
        return self.log(
            {
                "message": text,
                "level": "info",
            }
        )

    def debug(self, text: str, **_kwargs):
        return self.log({"message": text, "level": "debug"})

    def warning(self, text: str, **_kwargs):
        return self.log({"message": text, "level": "warning"})

    def error(self, text: str, **_kwargs):
        tb = traceback.format_exc()
        return self.log(
            {"message": str(text) + f"\nTraceback: {tb}" + "\n", "level": "error"}
        )

    def exception(self, text: str, **_kwargs):
        return self.error(text, **_kwargs)
