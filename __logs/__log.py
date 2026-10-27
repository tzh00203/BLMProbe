# -*- coding:utf-8 -*-

"""
Logging Utilities:
1. Initializes a logger that logs to both a file and the console.
2. Supports dynamic creation of directories for log files.
3. Provides a simple test function to demonstrate logging levels.
"""

import logging
import os


def log_init(log_filename: str) -> logging.Logger:
    """
    Initialize a logger that logs to both a file and the console.
    Args:
        log_filename (str): Path to the log file.
    Returns:
        logging.Logger: Configured logger instance.
    """
    import os
    import logging

    # Ensure the directory for the log file exists
    directory = os.path.dirname(log_filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    logger = logging.getLogger()

    # avoid add Handler again
    if not logger.hasHandlers():
        # Configure logging to file
        file_handler = logging.FileHandler(log_filename, mode='a')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(filename)s: %(lineno)d] : %(levelname)s \t%(message)s',
            datefmt='%Y-%m-%d %A %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Configure logging to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(filename)s: %(lineno)d] : %(levelname)s \t%(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logger.setLevel(logging.INFO)

    return logger


def log_out_test():
    """
    Test function to demonstrate different logging levels.
    Logs messages at DEBUG, INFO, WARNING, ERROR, and CRITICAL levels.
    """
    logging.debug('Logger debug message')
    logging.info('Logger info message')
    logging.warning('Logger warning message')
    logging.error('Logger error message')
    logging.critical('Logger critical message')


if __name__ == "__main__":
    # Initialize the logger (example file name: logs/example.log)
    logger = log_init("logs/example.log")

    # Log some test messages
    log_out_test()
