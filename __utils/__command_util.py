"""
Command Utilities:
1. Execute network and system commands like `nc` and `nmap`.
2. Manage command timeouts and execution results.
"""

import os
import subprocess
from subprocess import PIPE
from func_timeout import func_set_timeout
import func_timeout


def nc_command(port: int, filename: str, timeout_duration: int):
    """
    Execute a netcat command to listen on a specific port and save data to a file.
    Args:
        port (int): The port number to listen on.
        filename (str): The file to save the received data.
        timeout_duration (int): The timeout duration for the command in seconds.
    """
    cmd = f"timeout {timeout_duration} nc -lvp {port} > {filename}"
    subprocess.run(cmd, shell=True, stdout=PIPE, stderr=PIPE)


@func_set_timeout(1)  # Set a timeout of 1 second for the function execution
def nmap_command_limit(command: str) -> str:
    """
    Execute an `nmap` command with a strict timeout limit.
    Args:
        command (str): The `nmap` command to execute.
    Returns:
        str: The standard output of the command or 'failed' if unsuccessful.
    """
    result = subprocess.run(command, shell=True, stdout=PIPE, stderr=PIPE)
    if result.returncode == 0:
        return result.stdout.decode()
    return "failed"


def nmap_command(command: str) -> str:
    """
    Execute an `nmap` command with a timeout handler.
    Args:
        command (str): The `nmap` command to execute.
    Returns:
        str: The command output or 'failed' if the command times out or fails.
    """
    try:
        return nmap_command_limit(command)
    except func_timeout.exceptions.FunctionTimedOut:
        return "failed"


def common_command(command: str) -> str:
    """
    Execute a generic shell command and return the result.
    Args:
        command (str): The shell command to execute.
    Returns:
        str: The standard output of the command or 'failed' if unsuccessful.
    """
    result = subprocess.run(command, shell=True, stdout=PIPE, stderr=PIPE)
    if result.returncode == 0:
        return result.stdout.decode()
    return "failed"
