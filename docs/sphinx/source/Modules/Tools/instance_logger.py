import logging
from typing import Any
from datetime import datetime

default_logger_name = "qudns"


def change_logger_name(new_name: str):
    """
    Changes the qudns logger name.
    Call this before simulations.

    Args:
        new_name: New logger name string.

    Returns:
        None.
    """

    global default_logger_name
    default_logger_name = new_name


class SubLogger(object):
    """
    This object helps generating simulation result.
    Its a little wrapper of logging.
    """

    def __init__(self, host: Any) -> None:
        """
        Sub logger constructor.
        :param host: It may contain Any type, prefer a string.
        """

        self._host = host
        self._logger = logging.getLogger(default_logger_name)
        self._loglevel = self._logger.level
        self._logs: str = ""

    def warning(self, msg: str) -> None:
        """
        Logging.warning().
        :param msg: Message.
        :return: None.
        """

        if self._loglevel <= 30:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
            message = "{}: WARNING: {}\n".format(date_time, msg)
            self._logs += message
        self._logger.warning(msg)

    def info(self, msg: str) -> None:
        """
        Logging.info().
        :param msg: Message.
        :return: None.
        """

        if self._loglevel <= 20:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
            message = "{}: INFO: {}\n".format(date_time, msg)
            self._logs += message
        self._logger.info(msg)

    def debug(self, msg: str) -> None:
        """
        Logging.debug().
        :param msg: Message.
        :return: None.
        """

        if self._loglevel <= 10:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
            message = "{}: DEBUG: {}\n".format(date_time, msg)
            self._logs += message
        self._logger.debug(msg)

    def error(self, msg: str) -> None:
        """
        Logging.error().
        :param msg: Message.
        :return: None.
        """

        if self._loglevel <= 40:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
            message = "{}: ERROR: {}\n".format(date_time, msg)
            self._logs += message
        self._logger.error(msg)

    def critical(self, msg: str) -> None:
        """
        Logging.critical().
        :param msg: Message.
        :return: None.
        """

        if self._loglevel <= 50:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
            message = "{}: CRITICAL: {}\n".format(date_time, msg)
            self._logs += message
        self._logger.critical(msg)

    def log(self, msg: str, level: int) -> None:
        """
        Logging.log().
        :param msg: Message.
        :param level: level of logging.
        :return: None.
        """

        if self._loglevel <= level:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
            message = "{}: LOG: {}\n".format(date_time, msg)
            self._logs += message
        self._logger.log(level, msg)

    @property
    def logs(self) -> str:
        return self._logs

    @property
    def host(self) -> Any:
        return self._host

    @property
    def loglevel(self) -> int:
        return self._loglevel

    def __len__(self):
        lines = self._logs.splitlines()
        return lines.__len__()

    def __int__(self) -> int:
        return self._loglevel

    def __str__(self) -> str:
        try:
            to_str = str(self._host)
            return to_str
        except TypeError:
            return "host"


def get_logger() -> logging.Logger:
    """ Returns library logger"""

    return logging.getLogger(default_logger_name)
