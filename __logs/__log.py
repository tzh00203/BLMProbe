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
    # Ensure the directory for the log file exists
    directory = os.path.dirname(log_filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Configure logging to file
    logging.basicConfig(
        level=logging.DEBUG,  # Log level for file
        format='%(asctime)s [%(filename)s: %(lineno)d] : %(levelname)s \t%(message)s',  # Log format
        datefmt='%Y-%m-%d %A %H:%M:%S',  # Date format
        filename=log_filename,  # Log file name
        filemode='a'  # Append mode
    )

    # Configure logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Log level for console
    console_formatter = logging.Formatter(
        '%(asctime)s [%(filename)s: %(lineno)d] : %(levelname)s \t%(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Add console handler to the root logger
    logger = logging.getLogger()
    logger.addHandler(console_handler)

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
