""" 
Logger.py

Functions for setting up a customized logger.
"""

import logging
import os
from typing import Optional

def setup_logger(module_name: str, log_file: Optional[str] = None, level=logging.INFO):
    """
    Set up a logger with a console handler and an optional file handler.

    :param module_name: Name of the module for which the logger is configured.
    :param log_file: Path to the log file. If None, file logging is disabled.
    :param level: Logging level (e.g., logging.INFO, logging.DEBUG).
    :return: Configured logger instance.
    """
    # Ensure that log file directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(module_name)
    logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file is specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger