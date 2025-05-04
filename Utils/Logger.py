""" 
Logger.py

Functions for setting up a customized logger.
"""
import logging
import os
from typing import Optional


def setup_logger(module_name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with a console handler and an optional file handler.

    :param module_name: Name of the module for which the logger is configured.
    :param log_file: Path to the log file. If None, file logging is disabled.
    :param level: Logging level (e.g., logging.INFO, logging.DEBUG).
    
    :return: Configured logger instance.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    
    # Make sure directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    absolute_path = os.path.abspath(log_file)

    # Remove any existing FileHandler whose filename differs
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler) and getattr(handler, "baseFilename", None) != absolute_path:
            logger.removeHandler(handler)
            handler.close()

    # Add FileHandler for the specified path if it doesn't already exist
    if not any(
        isinstance(handler, logging.FileHandler) and handler.baseFilename == absolute_path for handler in logger.handlers
    ):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        file_handler = logging.FileHandler(absolute_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.log_file = file_handler.baseFilename

    return logger