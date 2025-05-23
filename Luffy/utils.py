import os
import sys

def clear_terminal():
    """
    Clears the terminal screen.
    Use 'cls' for Windows and 'clear' for Unix-based systems.
    """
    command = 'cls' if sys.platform.startswith('win') else 'clear'
    os.system(command)

def log_message(message, log_file="logs/detected_texts.txt"):
    """
    Appends a message to the specified log file.
    
    Parameters:
        message (str): The message to log.
        log_file (str): Path to the log file (default: logs/detected_texts.txt).
    """
    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(log_file, "a") as file:
        file.write(message + "\n")
