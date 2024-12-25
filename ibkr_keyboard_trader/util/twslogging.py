"""Utility functions for logging.

This module provides a function to setup the logger for logging messages to the terminal window and/or a file.
It provides a unified logging format for all the modules in the package and should be used in other related packages
to maintain consistency in logging. The name of the logger should be the name of the package.

Notes
-----
You only need to setup the logger once in the main module of the package. The logger can be retrieved in other modules
by calling `logging.getLogger(__package__)` to get the logger instance.
    
Examples
--------

    from betatrader.utils.logging import setup_logger
    
    logger = setup_logger(__package__)
    logger.info('This is an info message.')
    logger.debug('This is a debug message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')
    
    # You may setup the logger with different levels for the terminal and file.
    # It logs all levels equal or higher than the set level.
    import logging
    logger = setup_logger('my_package', logging.INFO, logging.DEBUG)
    
    # Avaliable log levels from the highest to the lowest:
    # CRITICAL = 50
    # FATAL = CRITICAL
    # ERROR = 40
    # WARNING = 30
    # WARN = WARNING
    # INFO = 20
    # DEBUG = 10
    # NOTSET = 0
    
    # Setting the level to None will disable the logging for that handler.
    logger = setup_logger('my_package', logging.INFO, None)
"""

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name: str = 'simulator',
                 screen_level: int | None = logging.WARN,
                 file_level: int | None = logging.DEBUG,
                 log_file: int | None = None) -> logging.Logger:
    """Setup logger for the package.

    Args:
        name (str, optional): Name of the logger to use. Defaults to 'betatrader'.
        screen_level ([int | None], optional): level of logging to be displayed in the terminal. Set to None to disable. Defaults to logging.WARN.
        file_level ([int | None], optional): level of logging to be logged in file. Set to None to disable. Defaults to logging.DEBUG.
        log_file ([int | None], optional): name of the file. Defaults to the name of the logger.

    Returns:
        logging.Logger: Logger instance.
    """

    logger = logging.getLogger(name)

    try:
        if logger.configured:
            return logger
    except AttributeError:
        pass

    if screen_level is None and file_level is None:
        return
    if screen_level is None:
        logger.setLevel(file_level)
    elif file_level is None:
        logger.setLevel(screen_level)
    else:
        logger.setLevel(min(screen_level, file_level))

    # Stream handler
    if screen_level is not None:
        s_handler = logging.StreamHandler()
        s_handler.setLevel(screen_level)
        s_format = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s::%(module)s::%(levelname)-8s: %(message)s', '%H:%M:%S')
        s_handler.setFormatter(s_format)
        logger.addHandler(s_handler)

    # File handler
    if file_level is not None:
        if log_file is None:
            log_file = os.path.join('.log', f'{name}.log')
        else:
            log_file = os.path.join('.log', log_file)
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        f_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=10)
        f_handler.setLevel(file_level)
        if name == "trade":
            f_format = logging.Formatter('%(message)s')
        else:
            f_format = logging.Formatter('%(asctime)s %(name)s::%(module)s::%(levelname)-8s: %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    logger.configured = True
    return logger
